/* Use only from an explicitly requested, authorized Figma Plugin API context. */
const TRIGGERS = new Set(['ON_CLICK', 'ON_HOVER', 'ON_PRESS', 'ON_DRAG', 'AFTER_TIMEOUT']);
const NAVIGATION = new Set(['NAVIGATE', 'OVERLAY', 'SWAP', 'SCROLL_TO', 'CHANGE_TO']);
const SIMPLE_TRANSITIONS = new Set(['DISSOLVE', 'SMART_ANIMATE', 'SCROLL_ANIMATE']);
const DIRECTIONAL_TRANSITIONS = new Set(['MOVE_IN', 'MOVE_OUT', 'PUSH', 'SLIDE_IN', 'SLIDE_OUT']);

const EASINGS = new Set(['EASE_IN', 'EASE_OUT', 'EASE_IN_AND_OUT', 'LINEAR', 'EASE_IN_BACK', 'EASE_OUT_BACK',
  'EASE_IN_AND_OUT_BACK', 'CUSTOM_CUBIC_BEZIER', 'GENTLE', 'QUICK', 'BOUNCY', 'SLOW', 'CUSTOM_SPRING']);
function fail(message) {
  throw new Error(message);
}

function stable(value) {
  if (Array.isArray(value)) return '[' + value.map(stable).join(',') + ']';
  if (value && typeof value === 'object') {
    return '{' + Object.keys(value).sort().map(key => JSON.stringify(key) + ':' + stable(value[key])).join(',') + '}';
  }
  return JSON.stringify(value);
}

function validateTrigger(trigger) {
  if (!trigger || !TRIGGERS.has(trigger.type)) fail('Unsupported or missing trigger');
  if (trigger.type === 'AFTER_TIMEOUT' && (!Number.isFinite(trigger.timeout) || trigger.timeout < 0)) {
    fail('AFTER_TIMEOUT requires a non-negative timeout in milliseconds');
  }
  const allowed = trigger.type === 'AFTER_TIMEOUT' ? new Set(['type', 'timeout']) : new Set(['type']);
  if (Object.keys(trigger).some(key => !allowed.has(key))) fail('Unexpected trigger fields');
}

function validateTransition(transition) {
  if (transition === null || transition === undefined) return;
  if (!transition || typeof transition !== 'object' || !Number.isFinite(transition.duration) || transition.duration < 0 ||
      !transition.easing || !EASINGS.has(transition.easing.type)) fail('Malformed or unsupported transition');
  if (transition.easing.type === 'CUSTOM_CUBIC_BEZIER') {
    const curve = transition.easing.easingFunctionCubicBezier;
    if (!curve || !['x1', 'y1', 'x2', 'y2'].every(key => Number.isFinite(curve[key]))) fail('Custom cubic easing needs four finite control points');
  }
  if (transition.easing.type === 'CUSTOM_SPRING') {
    const spring = transition.easing.easingFunctionSpring;
    if (!spring || !['mass', 'stiffness', 'damping', 'initialVelocity'].every(key => Number.isFinite(spring[key]))) {
      fail('Custom spring easing needs finite parameters');
    }
  }
  if (SIMPLE_TRANSITIONS.has(transition.type)) {
    if (transition.direction !== undefined || transition.matchLayers !== undefined) fail('Unexpected simple transition fields');
  } else if (DIRECTIONAL_TRANSITIONS.has(transition.type)) {
    if (!['LEFT', 'RIGHT', 'TOP', 'BOTTOM'].includes(transition.direction) || typeof transition.matchLayers !== 'boolean') {
      fail('Directional transitions require direction and matchLayers');
    }
  } else {
    fail('Unsupported transition type: ' + transition.type);
  }
}

function makeReaction(edge) {
  validateTrigger(edge.trigger);
  let action;
  if (edge.action === 'BACK' || edge.action === 'CLOSE') {
    if (edge.to !== undefined || edge.navigation !== undefined || edge.transition !== undefined) {
      fail(edge.action + ' does not accept a destination, navigation, or transition');
    }
    action = { type: edge.action };
  } else {
    if (edge.action !== undefined && edge.action !== 'NODE') fail('Unsupported action: ' + edge.action);
    if (typeof edge.to !== 'string' || !edge.to || !NAVIGATION.has(edge.navigation)) fail('NODE action needs destination and supported navigation');
    validateTransition(edge.transition);
    action = { type: 'NODE', destinationId: edge.to, navigation: edge.navigation,
      transition: edge.transition === undefined ? null : edge.transition };
  }
  return { trigger: edge.trigger, actions: [action] };
}

function readActions(reaction) {
  return reaction.actions || (reaction.action ? [reaction.action] : []);
}

function matchesTrigger(actual, expected) {
  return Boolean(actual && actual.type === expected.type &&
    (expected.type !== 'AFTER_TIMEOUT' || actual.timeout === expected.timeout));
}

function matchesTransition(actual, expected) {
  if (expected === null) return actual == null;
  if (!actual || actual.type !== expected.type || !Number.isFinite(actual.duration) ||
      Math.abs(actual.duration - expected.duration) > 0.00001 ||
      !actual.easing || actual.easing.type !== expected.easing.type) return false;
  if (DIRECTIONAL_TRANSITIONS.has(expected.type) &&
      (actual.direction !== expected.direction || actual.matchLayers !== expected.matchLayers)) return false;
  if (expected.easing.type === 'CUSTOM_CUBIC_BEZIER' &&
      stable(actual.easing.easingFunctionCubicBezier) !== stable(expected.easing.easingFunctionCubicBezier)) return false;
  if (expected.easing.type === 'CUSTOM_SPRING' &&
      stable(actual.easing.easingFunctionSpring) !== stable(expected.easing.easingFunctionSpring)) return false;
  return true;
}

function matchesPersisted(actual, expected) {
  const actualActions = readActions(actual);
  if (!matchesTrigger(actual && actual.trigger, expected.trigger) || actualActions.length !== 1) return false;
  const actualAction = actualActions[0];
  const expectedAction = expected.actions[0];
  if (actualAction.type !== expectedAction.type) return false;
  if (actualAction.type === 'NODE') {
    return actualAction.destinationId === expectedAction.destinationId &&
      actualAction.navigation === expectedAction.navigation &&
      matchesTransition(actualAction.transition || null, expectedAction.transition);
  }
  return true;
}

function preservesExisting(actual, expected) {
  return matchesTrigger(actual && actual.trigger, expected.trigger) &&
    stable(readActions(actual)) === stable(readActions(expected));
}

/** Append a user-authorized graph. Returns Plugin API readback, not preview evidence. */
export async function applyPrototypeGraph(figma, graph, authorized) {
  if (authorized !== true) fail('Explicit prototype authorization is required');
  if (!figma || !Array.isArray(graph && graph.edges) || graph.edges.length === 0) fail('Graph must contain at least one edge');
  const prepared = new Map();
  const seenEdges = new Set();
  for (const edge of graph.edges) {
    if (!edge || typeof edge.from !== 'string' || !edge.from) fail('Every edge needs a source node ID');
    const reaction = makeReaction(edge);
    const signature = edge.from + '|' + stable(reaction);
    if (seenEdges.has(signature)) fail('Duplicate edge in graph for source ' + edge.from);
    seenEdges.add(signature);
    if (!prepared.has(edge.from)) prepared.set(edge.from, []);
    prepared.get(edge.from).push(reaction);
  }

  const nodes = new Map();
  const before = new Map();
  for (const [id, additions] of prepared) {
    const node = typeof figma.getNodeByIdAsync === 'function'
      ? await figma.getNodeByIdAsync(id)
      : figma.getNodeById(id);
    if (!node || !Array.isArray(node.reactions) || typeof node.setReactionsAsync !== 'function') {
      fail('Source node is missing or does not support reactions: ' + id);
    }
    const original = JSON.parse(JSON.stringify(node.reactions));
    const next = original.concat(additions);
    for (const addition of additions) {
      if (original.some(item => matchesPersisted(item, addition))) {
        fail('Requested edge already exists on source node ' + id);
      }
    }
    nodes.set(id, node);
    before.set(id, { original, additions, next });
  }
  for (const [id, { next }] of before) {
    for (const reaction of next) {
      for (const action of readActions(reaction)) {
        if (action.type === 'NODE' && !nodes.has(action.destinationId)) {
          const target = typeof figma.getNodeByIdAsync === 'function'
            ? await figma.getNodeByIdAsync(action.destinationId)
            : figma.getNodeById(action.destinationId);
          if (!target) fail('Destination node is missing: ' + action.destinationId);
        }
      }
    }
  }

  const attempted = [];
  try {
    for (const [id, record] of before) {
      attempted.push(id);
      await nodes.get(id).setReactionsAsync(record.next);
      const persisted = nodes.get(id).reactions;
      if (!Array.isArray(persisted) || persisted.length !== record.next.length ||
          !record.original.every((reaction, index) => preservesExisting(persisted[index], reaction)) ||
          !record.additions.every((edge, offset) => matchesPersisted(persisted[persisted.length - record.additions.length + offset], edge))) {
        fail('Plugin API reaction readback mismatch for source ' + id);
      }
    }
  } catch (error) {
    const rollbackErrors = [];
    for (const id of attempted.reverse()) {
      try {
        await nodes.get(id).setReactionsAsync(before.get(id).original);
      } catch (rollbackError) {
        rollbackErrors.push(id + ': ' + String(rollbackError));
      }
    }
    if (rollbackErrors.length) {
      fail(String(error) + '; rollback was incomplete: ' + rollbackErrors.join('; '));
    }
    throw error;
  }

  return {
    status: 'persisted-readback-not-preview-tested',
    nodes: Array.from(before, ([id, record]) => ({
      id,
      added: record.additions.length,
      persistedReactions: JSON.parse(JSON.stringify(nodes.get(id).reactions))
    }))
  };
}
