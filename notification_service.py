import json
import os


class Message:
    @staticmethod
    def error_out(title, ci_title="", runner_not_available=False, runner_failed=False, setup_failed=False):
        blocks = []
        title_block = {"type": "header", "text": {"type": "plain_text", "text": title}}
        blocks.append(title_block)

        if ci_title:
            ci_title_block = {"type": "section", "text": {"type": "mrkdwn", "text": ci_title}}
            blocks.append(ci_title_block)

        offline_runners = []
        if runner_not_available:
            text = "💔 CI runners are not available! Tests are not run. 😭"
            result = os.environ.get("OFFLINE_RUNNERS")
            if result is not None:
                try:
                    offline_runners = json.loads(result)
                except json.decoder.JSONDecodeError:
                    offline_runners = []
        elif runner_failed:
            text = "💔 CI runners have problems! Tests are not run. 😭"
        elif setup_failed:
            text = "💔 Setup job failed. Tests are not run. 😭"
        else:
            text = "💔 There was an issue running the tests. 😭"

        error_block_1 = {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": text,
            },
        }

        text = ""
        if len(offline_runners) > 0:
            text = "\n  • " + "\n  • ".join(offline_runners)
            text = f"The following runners are offline:\n{text}\n\n"
        text += "🙏 Let's fix it ASAP! 🙏"

        error_block_2 = {
            "type": "section",
            "text": {
                "type": "plain_text",
                "text": text,
            },
            "accessory": {
                "type": "button",
                "text": {"type": "plain_text", "text": "Check Action results", "emoji": True},
                "url": f"https://github.com/huggingface/transformers/actions/runs/{os.environ['GITHUB_RUN_ID']}",
            },
        }
        blocks.extend([error_block_1, error_block_2])

        payload = json.dumps(blocks)

        print("Sending the following payload")
        print(json.dumps({"blocks": blocks}))

        client.chat_postMessage(
            channel=os.environ["CI_SLACK_REPORT_CHANNEL_ID"],
            text=text,
            blocks=payload,
        )

    def post(self):
        payload = self.payload
        print("Sending the following payload")
        print(json.dumps({"blocks": json.loads(payload)}))

        text = f"{self.n_failures} failures out of {self.n_tests} tests," if self.n_failures else "All tests passed."

        self.thread_ts = client.chat_postMessage(
            channel=os.environ["CI_SLACK_REPORT_CHANNEL_ID"],
            blocks=payload,
            text=text,
        )

    # Rest of the code...

def retrieve_artifact(artifact_path: str, gpu: Optional[str]):
    if gpu not in [None, "single", "multi"]:
        raise ValueError(f"Invalid GPU for artifact. Passed GPU: `{gpu}`.")

    _artifact = {}

    if os.path.exists(artifact_path):
        files = os.listdir(artifact_path)
        for file in files:
            try:
                with open(os.path.join(artifact_path, file)) as f:
                    _artifact[file.split(".")[0]] = f.read()
            except UnicodeDecodeError as e:
                raise ValueError(f"Could not open {os.path.join(artifact_path, file)}.") from e

    return _artifact

def retrieve_available_artifacts():
    # Rest of the code...

# Rest of the code...
