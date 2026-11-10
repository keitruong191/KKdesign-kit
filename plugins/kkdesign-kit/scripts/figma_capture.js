// Read-only Figma Plugin API capture. Run in an authenticated Figma plugin context.
// Keep FIGMA_NODE_IDS explicit and limited to the public/design-system nodes needed.
const FIGMA_NODE_IDS = [];
const FIGMA_MAX_STYLES = 2;
const FIGMA_MAX_VARIABLES = 2;


if (FIGMA_NODE_IDS.length === 0) {
  throw new Error('FIGMA_NODE_IDS must contain at least one explicitly authorized node ID.');
}

(async () => {
  const allowedNodeFields = [
    'id', 'name', 'type', 'visible', 'locked', 'opacity', 'blendMode',
    'absoluteBoundingBox', 'relativeTransform', 'constraints', 'layoutMode',
    'primaryAxisSizingMode', 'counterAxisSizingMode', 'primaryAxisAlignItems',
    'counterAxisAlignItems', 'paddingLeft', 'paddingRight', 'paddingTop',
    'paddingBottom', 'itemSpacing', 'fills', 'strokes', 'strokeWeight',
    'strokeAlign', 'effects', 'cornerRadius', 'rectangleCornerRadii',
    'characters', 'characterStyleOverrides', 'style', 'componentId',
    'componentPropertyDefinitions', 'componentProperties', 'variantProperties',
    'mainComponent'
  ];

  let truncatedValues = 0;
  let unavailableProperties = 0;

  function copyValue(value, depth = 0, seen = new WeakSet()) {
    if (value === null || typeof value === 'string' || typeof value === 'boolean') return value;
    if (typeof value === 'number') return Number.isFinite(value) ? value : null;
    if (typeof value !== 'object') return null;
    if (depth >= 12 || seen.has(value)) {
      truncatedValues += 1;
      return null;
    }
    seen.add(value);
    if (Array.isArray(value)) return value.map(item => copyValue(item, depth + 1, seen));
    const result = {};
    for (const key of Object.keys(value)) {
      const item = value[key];
      if (typeof item !== 'function' && item !== undefined) result[key] = copyValue(item, depth + 1, seen);
    }
    return result;
  }

  async function serializeNode(node, depth = 0) {
    const result = {};
    for (const field of allowedNodeFields) {
      if (field === 'mainComponent') {
        if (node.type === 'INSTANCE') {
          try {
            const mainComponent = await node.mainComponent;
            result.mainComponent = { id: mainComponent?.id ?? null };
          } catch (_) {
            unavailableProperties += 1;
          }
        }
        continue;
      }
      try {
        const value = node[field];
        if (value !== undefined && typeof value !== 'function') result[field] = copyValue(value);
      } catch (_) {
        unavailableProperties += 1;
      }
    }
    if (depth < 12 && 'children' in node) {
      result.children = [];
      for (const child of node.children) result.children.push(await serializeNode(child, depth + 1));
    } else if ('children' in node) {
      truncatedValues += 1;
    }
    return result;
  }

  const documentChildren = [];
  const missingNodeIds = [];
  for (const id of FIGMA_NODE_IDS) {
    const node = await figma.getNodeByIdAsync(id);
    if (node) documentChildren.push(await serializeNode(node));
    else missingNodeIds.push(id);
  }

  const components = [];
  const componentSets = [];
  const seenNodeIds = new Set();
  async function collectComponents(node) {
    if (seenNodeIds.has(node.id)) return;
    seenNodeIds.add(node.id);
    if (node.type === 'COMPONENT' || node.type === 'COMPONENT_SET') {
      const entry = {
        key: node.key,
        name: node.name,
        description: node.description,
        nodeId: node.id,
        remote: node.remote,
        documentationLinks: copyValue(node.documentationLinks || []),
        componentPropertyDefinitions: copyValue(node.componentPropertyDefinitions || {})
      };
      if (node.type === 'COMPONENT_SET') componentSets.push(entry);
      else components.push(entry);
    }
    if ('children' in node) {
      for (const child of node.children) await collectComponents(child);
    }
  }
  for (const id of FIGMA_NODE_IDS) {
    const node = await figma.getNodeByIdAsync(id);
    if (node) await collectComponents(node);
  }

  const styleGetters = [
    ['PAINT', async () => figma.getLocalPaintStylesAsync ? figma.getLocalPaintStylesAsync() : figma.getLocalPaintStyles()],
    ['TEXT', async () => figma.getLocalTextStylesAsync ? figma.getLocalTextStylesAsync() : figma.getLocalTextStyles()],
    ['EFFECT', async () => figma.getLocalEffectStylesAsync ? figma.getLocalEffectStylesAsync() : figma.getLocalEffectStyles()],
    ['GRID', async () => figma.getLocalGridStylesAsync ? figma.getLocalGridStylesAsync() : figma.getLocalGridStyles()]
  ];
  const allStyles = [];
  for (const [styleType, getStyles] of styleGetters) {
    try {
      for (const style of await getStyles()) allStyles.push({ styleType, style });
    } catch (_) {
      unavailableProperties += 1;
    }
  }
  allStyles.sort((a, b) => String(a.style.id || a.style.key).localeCompare(String(b.style.id || b.style.key)));
  const totalStyles = allStyles.length;
  const styles = [];
  for (const { styleType, style } of allStyles.slice(0, FIGMA_MAX_STYLES)) {
    const entry = {
      key: style.key,
      name: style.name,
      description: style.description,
      styleType,
      nodeId: style.id,
      remote: style.remote
    };
    if (styleType === 'PAINT') entry.paints = copyValue(style.paints);
    if (styleType === 'TEXT') {
      entry.textStyle = {};
      for (const field of ['fontName', 'fontSize', 'lineHeight', 'letterSpacing', 'textCase', 'textDecoration', 'paragraphIndent', 'paragraphSpacing', 'listOptions']) {
        try {
          if (style[field] !== undefined) entry.textStyle[field] = copyValue(style[field]);
        } catch (_) {
          unavailableProperties += 1;
        }
      }
    }
    if (styleType === 'EFFECT') entry.effects = copyValue(style.effects);
    if (styleType === 'GRID') entry.grids = copyValue(style.layoutGrids);
    styles.push(entry);
  }

  let variables;
  let totalVariables = null;
  try {
    const localVariables = await figma.variables.getLocalVariablesAsync();
    const selectedVariables = localVariables
      .slice()
      .sort((a, b) => String(a.id).localeCompare(String(b.id)))
      .slice(0, FIGMA_MAX_VARIABLES);
    totalVariables = localVariables.length;
    const selectedIds = new Set(selectedVariables.map(variable => variable.id));
    const collectionIds = new Set(selectedVariables.map(variable => variable.variableCollectionId));
    const localCollections = await figma.variables.getLocalVariableCollectionsAsync();
    variables = {
      variables: selectedVariables.map(variable => ({
        id: variable.id,
        key: variable.key,
        name: variable.name,
        description: variable.description,
        resolvedType: variable.resolvedType,
        valuesByMode: copyValue(variable.valuesByMode),
        variableCollectionId: variable.variableCollectionId,
        scopes: copyValue(variable.scopes),
        codeSyntax: copyValue(variable.codeSyntax)
      })),
      variableCollections: localCollections
        .filter(collection => collectionIds.has(collection.id))
        .map(collection => ({
          id: collection.id,
          key: collection.key,
          name: collection.name,
          modes: copyValue(collection.modes),
          defaultModeId: collection.defaultModeId,
          variableIds: collection.variableIds.filter(id => selectedIds.has(id)),
          remote: collection.remote
        }))
    };
  } catch (_) {
    // Access to variables is optional; absence must remain visible to the adapter.
  }


  return {
    schemaVersion: '1.0.0',
    kind: 'figma-capture',
    fileKey: figma.fileKey || null,
    version: null,
    lastModified: null,
    document: { id: '0:0', name: figma.root.name, type: 'DOCUMENT', children: documentChildren },
    components,
    componentSets,
    styles,
    ...(variables === undefined ? {} : { variables }),
    missingNodeIds,
    captureCounts: { styles: { total: totalStyles, returned: styles.length, limit: FIGMA_MAX_STYLES },
      variables: { total: totalVariables, returned: variables ? variables.variables.length : 0, limit: FIGMA_MAX_VARIABLES } },
    limitations: [
      'Components and component sets are limited to the explicitly selected node subtrees.',
      'Styles and local variables are file-wide Plugin API snapshots limited by FIGMA_MAX_STYLES and FIGMA_MAX_VARIABLES.',
      'The Plugin API does not expose a REST revision or last-modified timestamp in this capture.'
    ],
    truncatedValues,
    unavailableProperties
  };
})()

