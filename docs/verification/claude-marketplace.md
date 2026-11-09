# WWA-01 native verification

Implementation/code verification: **ready for coordinator review and integration**.
Authenticated native menu/Setup acceptance: **pending**. The prior attempts
failed because the isolated profile lacked Claude authentication; they are not
native menu passes or release acceptance.

The owner explicitly separated acceptance requiring unavailable resources from
code integration. The coordinator may merge reviewed, tested implementation to
`feature/marketplace-installation-setup` while recording native acceptance as
pending. The owner will arrange an authenticated installation and feedback;
pending external acceptance does not block code integration. This does not
authorize a merge to main or publication.

Environment: macOS ARM64, Python 3.9 development venv with `requirements.txt`,
Claude Code `2.1.308`. No primary provider configuration or credentials were
read/copied/modified. Native commands used a fresh temporary HOME,
USERPROFILE and `CLAUDE_CONFIG_DIR`, an unrelated temporary product CWD with
spaces, and no inherited provider credentials. Source and output paths below
are placeholders for temporary locations, not published install endpoints.

## Observed acceptance

| Criterion | Evidence | Verdict |
| --- | --- | --- |
| Clean native marketplace registration/install at the correct version, without end-user clone or standalone installer | Actual Git smart HTTP loopback source from the built marketplace ZIP; native registration/install exit 0; native inventory reports enabled user-scope `kkdesign-kit@kkdesign-kit-marketplace`, version `0.5.0a1`, under provider cache. | Met for local native packaging review; public publication is not claimed. |
| Actual Claude session discovers namespaced skill and opens menu with Setup without Python just to read it | Session init lists `kkdesign-kit:kkdesign-kit` in both `skills` and `slash_commands`, and plugin version `0.5.0a1`. Both bare invocation and Setup attempt stop with `authentication_failed` / `Not logged in · Please run /login` before rendering. | Pending authenticated acceptance: native discovery observed; rendered menu/Setup not observed. |
| Canonical complete resources at arbitrary provider cache location without original checkout or standalone copy | Built payload uses the existing allowlist and canonical bytes, plus plugin metadata covered by bundle integrity. Extracted verifier runs from the native cache after removal of the temporary packaged source and transport: 57 files, 35 required resources verified. Native component inventory still works; no standalone skill is created. | Packaging/resource relocation observed; helper workflows intentionally blocked pending runtime integration. |
| Missing runtime says Setup required; native uninstall preserves project data | Bundled instructions specify Setup required; launcher refuses helper execution. Native uninstall exits 0, installed inventory becomes empty, and synthetic DESIGN/lesson/task-history/user-runtime sentinels survive. | Native lifecycle preservation observed; actual menu readiness message remains unverified due to authentication. |
| Real install → discovery → menu proof | Native install and real-session discovery succeeded. No model/tool execution occurred before the auth failure, and no menu response was produced. | Pending authenticated acceptance; schema checks are not substituted for menu proof. |

## Checks and commands

`python -m unittest discover -s tests -v` in the dependency-equipped external
development venv: **128 tests passed**, including four marketplace tests for
deterministic allowlisted output, relocated verification/tampering, refusing
helper execution without plugin runtime support, no overwrite and version drift.

The following native evidence comes from the earlier packaging smoke, before
the continuation's test-policy cleanup and documentation-only changes. The
continuation reruns the unit suite once; it does not repeat the known failing
native-auth scenario or claim a new native pass.

The temporary native smoke performed these real commands in order:

```text
python scripts/build_claude_marketplace.py --output <temporary-marketplace.zip>
claude --version
claude plugin validate <extracted-marketplace>
claude plugin marketplace add <loopback-smart-http-git-url> --scope user
claude plugin install kkdesign-kit@kkdesign-kit-marketplace --scope user
claude plugin list --json
# Remove original packaged source and stop its Git transport.
claude plugin details kkdesign-kit@kkdesign-kit-marketplace
python -I -B <cached-plugin>/scripts/kkdesign_install.py verify --source <cached-plugin>
python -B <cached-plugin>/scripts/kkdesign_run.py materialize_example --output <temporary-project>/must-not-be-created
claude auth status
claude --print /kkdesign-kit:kkdesign-kit --output-format stream-json --verbose --no-session-persistence --strict-mcp-config --setting-sources user --permission-mode dontAsk --allowedTools Read Skill --tools Read,Skill --no-chrome
claude --print '/kkdesign-kit:kkdesign-kit Setup' --output-format stream-json --verbose --no-session-persistence --strict-mcp-config --setting-sources user --permission-mode dontAsk --allowedTools Read Skill --tools Read,Skill --no-chrome
claude plugin uninstall kkdesign-kit@kkdesign-kit-marketplace --scope user
claude plugin list --json
```

Build, validation, registration, installation, inventory, component details and
uninstall returned 0. The cached verifier returned 0; the launcher guard returned
1 with Setup required and did not create the helper's output. Plugin bytes were
unchanged after both session attempts, and no user runtime was provisioned.
Authentication status returned 1 with `loggedIn: false`,
`authMethod: none`; both session attempts returned 1 with the authentication
error. Their actual init records show the namespaced skill from the installed
cache. They are discovery evidence, not menu evidence. The only enabled tools
in those sessions were Read and Skill; no Python tool was offered for menu use.

Native uninstall removed the installed/enabled registration (inventory `[]`).
Claude retained its cached payload directory; the plugin does not override the
host's cache retention or promise immediate physical cache deletion. Synthetic
project files and the separate synthetic user-cache sentinel remained intact.

Initial transport checks also found that native marketplace registration rejects
`file://`, and that dumb HTTP lacks shallow-clone support. Those are smoke
transport limitations, resolved by serving the unmodified packaged Git bytes
through Git's native smart HTTP backend on loopback.

## Pending external acceptance

Repeat native install/discovery, bare menu and Setup rendering in an isolated
profile with explicitly authorized authentication. Confirm the actual menu's
Setup-required state and no provisioning on either read-only route. Do not
copy credentials from a primary profile to work around this resource limitation. Automatic
runtime Setup, OS provisioning, managed plugin launcher, update compatibility,
migration, public publication and broader provider/platform support remain
outside WWA-01. The implementation is ready for coordinator review and may be
integrated under the owner's clarified policy, with authenticated native menu
acceptance still pending. Do not mark that external acceptance passed or publish
the plugin based on this evidence. This worker does not merge the PR or main.
