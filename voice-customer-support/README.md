# Voice Customer Support

A customer support voice agent that answers from your knowledge base in **connic retrieval**. Callers can ask product questions, work through documented troubleshooting, and request a sample support ticket. The agent searches your support content before answering and asks for confirmation before calling the ticket tool.

**Ticket creation is mocked.** The tool returns a `DEMO-…` receipt without saving a helpdesk ticket or notifying anyone. Tool inputs and results can still appear in connic run traces. Use fictional customer details when trying the example.

This template uses `gemini/gemini-3.8-live` with your own Google Gemini credentials. connic manages the voice runtime; model access and billing are through your provider. Add your customer knowledge to Retrieval in the deployment environment before the first call.

```bash
pip install --upgrade connic-composer-sdk
connic init my-voice-support --templates=voice-customer-support
cd my-voice-support
connic lint
python -m unittest discover -s tests -p 'test_voice_support.py'
```

Use a composer SDK release that supports `voice_config`. When working from this repository before the template is published, run the commands inside `voice-customer-support/` directly instead of fetching it with `connic init`.

## How it works

1. The agent greets the caller and asks what they need. Replies are short, with one question or a few troubleshooting steps at a time.
2. `voice_support.search_knowledge_base` calls connic's `retrieval_query` in the `support` namespace, including its child namespaces, requesting up to three relevant passages. It returns the full Retrieval response, preserving source IDs, scores, metadata, and any lookup error. The agent has read-only access; customer knowledge is managed in Retrieval, outside the example project.
3. If the answer is missing, the lookup fails, documented steps fail, or the caller asks for human help, the agent offers a demo ticket. It distinguishes a failed lookup from a search with no relevant results. It collects an issue summary, attempted steps, and a fictional email address, then reads them back for confirmation.
4. `voice_support.create_mock_ticket` validates the details and confirmation flag, then returns a simulated receipt. Identical inputs in the same run produce the same demo reference. Nothing is stored in a helpdesk and no human handoff occurs.
5. The agent explains the result and says goodbye when the caller is finished. connic lets the farewell play before ending the call.

The assistant can explain documented account actions; it cannot inspect accounts, issue refunds, change subscriptions, check live outages, or transfer a call to a person.

## connic features used

| Feature | Where |
|---------|-------|
| Native realtime voice model | `gemini/gemini-3.8-live` with `voice_config` |
| Managed semantic retrieval | Read-only `retrieval_query` over customer content in the `support` namespace |
| Python tools | Knowledge lookup and mocked ticket creation in `tools/voice_support.py` |
| Context injection | The mock receipt includes the current `run_id` without asking the caller for it |
| Conversation controls | Greeting, caller interruptions, turn detection, thinking sound, and idle timeout |
| Incoming phone calls | connic connectors link calls to the deployed agent |
| Runs and traces | Inspect speech transcripts and tool execution after a call; Gemini uses native transcription |

## Knowledge base setup

1. Select the project and the same environment you will deploy the voice agent to. Open its **Retrieval** tab. Retrieval content is scoped to the active environment.
2. Choose **Add content**, paste your support text or upload your documents, and set **Namespace** to `support`. You can also use child namespaces such as `support.billing`. Alternatively, open **Retrieval > Sources**, connect your existing documentation source or website, and choose `support` as its namespace.
3. For uploads, check the **Ingestion Activity** panel and wait for indexing to complete. For connected sources, use **Sync now** and inspect the source run for errors and indexed content.
4. Use **Search** on the Retrieval page with the `support` namespace to check representative customer questions before calling the agent.

The template contains no knowledge documents or seeding script. Populate and maintain the customer knowledge base directly in connic retrieval. See the [Retrieval setup guide](https://connic.co/docs/v1/platform/retrieval) for supported formats and source connections.

## Connector setup

1. In **Project Settings > LLM Provider**, save Google Gemini credentials with access to the configured native audio model.
2. For a project without a connected Git repository, run `connic login` from the example project and enter its login token from the dashboard. Run `connic deploy` to deploy to the default environment, or `connic deploy --env <environment-id>` for a specific environment. For a project connected to Git, deploy through its Git integration instead.
3. Add an incoming-call connector to the deployed `voice-customer-support` agent. Each voice connector links to exactly one deployed voice agent.
4. Once your support content is indexed in that environment, call the connected number. Afterward, open the resulting run to inspect transcripts, the knowledge lookup, and any mock ticket result.

Choose an incoming-call connector from [connic connectors](https://connic.co/docs/v1/connectors) and follow its setup guide to connect your phone number.

Phone provider and model usage charges still apply to live demos, even though the ticket tool is mocked.

## Try a conversation

Use questions based on the documents you added to Retrieval; the template does not define product policies or troubleshooting steps.

| Try | Expected behavior |
|-----|-------------------|
| Ask a product question covered by your support documents. | Searches `support` and explains the relevant retrieved passages in the caller's language. |
| Describe an issue with troubleshooting steps in your documentation. | Searches for those steps, walks through them briefly, and checks whether they helped. |
| Ask about something your documentation does not cover. | Searches, clarifies as needed, and acknowledges missing information without inventing an answer. |
| “Those steps didn't work. Please create a demo ticket for Alex at alex@example.com.” | Reads back the issue and email, explains that no real request will be sent, and waits for confirmation. |
| “Yes, those details are correct. Create the sample ticket.” | Calls `create_mock_ticket` and explains that the resulting receipt is simulated. |

Also try interrupting a spoken reply, declining ticket creation, correcting a misheard email, and saying goodbye.

## Customize it

- **Company and knowledge:** Update the prompt and greeting for your organization. Maintain its support documents through Retrieval uploads or synced sources. If you already use a different namespace, change the fixed `namespace="support"` in `search_knowledge_base` to match it. The caller cannot choose a namespace through the tool. See the [Retrieval tool reference](https://connic.co/docs/v1/build/tools/retrieval).
- **Real tickets:** Replace `create_mock_ticket` with your helpdesk API integration and configure its credentials in the project. Preserve confirmation and handle retries before enabling real writes. Update the tool name, prompt, greeting, and demo disclaimers to describe its actual behavior.
- **Model provider:** Change `model` to a supported native realtime model under `openai/`, `azure/`, `gemini/`, or `vertex_ai/` and configure matching credentials. Provider-specific voice names and model access vary. For OpenAI or Azure user transcripts, configure `voice_config.transcription_model`; see the [Voice reference](https://connic.co/docs/v1/build/voice). Managed `connic/*` models are not supported for voice.
- **Conversation:** Adjust `voice_config` for your greeting, voice, turn timing, interruptions, and idle timeout. Set `hang_up_allowed: false` if the agent should never end the conversation itself.

After `connic init`, agent files live under `agents/voice-customer-support/` and tool files remain under `tools/`. Customer knowledge stays in the selected environment's Retrieval index.

## Verification

```bash
connic lint
python -m unittest discover -s tests -p 'test_voice_support.py' -v
```

The offline tests mock `retrieval_query` and verify its namespace and result limit, unchanged results and errors, and exception propagation. They also verify confirmation, field validation, and deterministic mock receipts without network access or ticket storage. They use Python's standard `unittest` runner and the installed connic SDK; no Retrieval service or provider credentials are needed. `connic lint` validates the agent and tool definitions with the installed SDK.

## Structure

```text
voice-customer-support/
  agents/
    voice-customer-support.yaml
  tools/
    voice_support.py
  tests/
    test_voice_support.py
  requirements.txt
  README.md
```
