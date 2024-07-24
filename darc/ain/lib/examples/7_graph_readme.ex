defmodule ReadmeGraphExample do
  def run do
    # readme_content = "# fastui-chat\n\nA minimalistic ChatBot Interface in pure python. </br>\nBuild on top of [FastUI](https://github.com/pydantic/FastUI) and [LangChain Core](https://github.com/langchain-ai/langchain).\n\n## Usage\n\n```bash\npip install fastui-chat\n```\n\n```python\nfrom langchain.chat_models import ChatOpenAI\nfrom langchain.memory import ChatMessageHistory\n\nfrom fastui_chat import ChatUI, basic_chat_handler\n\nhistory = ChatMessageHistory()\nhandler = basic_chat_handler(\n    llm=ChatOpenAI(),\n    chat_history=history,\n)\n\nhistory.add_ai_message(\"How can I help you today?\")\n\napp = ChatUI(\n    chat_history=history,\n    chat_handler=handler,\n)\n\napp.start_with_uvicorn()\n```\n\n## Features\n\n- Easy to use\n- Minimalistic & Lightweight\n- LangChain Compatible\n- Python Only"
    readme_content = "# CVE-2023-44487\nBasic vulnerability scanning to see if web servers may be vulnerable to CVE-2023-44487\n\nThis tool checks to see if a website is vulnerable to CVE-2023-44487 completely non-invasively.\n\n1. The tool checks if a web server accepts HTTP/2 requests without downgrading them\n2. If the web server accepts and does not downgrade HTTP/2 requests the tool attempts to open a connection stream and subsequently reset it\n3. If the web server accepts the creation and resetting of a connection stream then the server is definitely vulnerable, if it only accepts HTTP/2 requests but the stream connection fails it may be vulnerable if the server-side capabilities are enabled.\n\nTo run,\n\n    $ python3 -m pip install -r requirements.txt\n\n    $ python3 cve202344487.py -i input_urls.txt -o output_results.csv\n\nYou can also specify an HTTP proxy to proxy all the requests through with the `--proxy` flag\n\n    $ python3 cve202344487.py -i input_urls.txt -o output_results.csv --proxy http://proxysite.com:1234\n\nThe script outputs a CSV file with the following columns\n\n- Timestamp: a timestamp of the request\n- Source Internal IP: The internal IP address of the host sending the HTTP requests\n- Source External IP: The external IP address of the host sending the HTTP requests\n- URL: The URL being scanned\n- Vulnerability Status: \"VULNERABLE\"/\"LIKELY\"/\"POSSIBLE\"/\"SAFE\"/\"ERROR\"\n- Error/Downgrade Version: The error or the version the HTTP server downgrades the request to\n\n*Note: \"Vulnerable\" in this context means that it is confirmed that an attacker can reset the a stream connection without issue, it does not take into account implementation-specific or volume-based detections*"

    actor_specs = generate_actor_specs()

    {:ok, _supervisor} = Ain.ActorSupervisor.start_link(actor_specs)

    # Allow some time for the actors to start
    :timer.sleep(1_000)

    actor_pids = for %{uuid: uuid} <- actor_specs do
      pid = GenServer.whereis({:global, uuid})
      {uuid, pid}
    end

    {reposketcher_uuid, reposketcher_pid} = Enum.at(actor_pids, 0)
    file_sketcher_pids = Enum.slice(actor_pids, 1, 3)
    sketch_fillers = Enum.slice(actor_pids, 4, 6)
    for {file_sketcher_uuid, file_sketcher_pid} <- file_sketcher_pids do
      connect_actors(reposketcher_pid, file_sketcher_pid, file_sketcher_uuid, actor_specs)
    end

    # 连接每个 file_sketcher 到每个 sketch_filler
    for {file_sketcher_uuid, file_sketcher_pid} <- file_sketcher_pids do
      for {sketch_filler_uuid, sketch_filler_pid} <- sketch_fillers do
        connect_actors(file_sketcher_pid, sketch_filler_pid, sketch_filler_uuid, actor_specs)
      end
    end

    # IO.inspect(actor_pids)
    message = %Message{
      sender: self(),
      receiver: self(),
      content: readme_content,
      parameters: %{},
      timestamp: :os.system_time(:millisecond),
      uuid: UUID.uuid4()
    }
    GenServer.cast(reposketcher_pid, {:receive, message})
  end

  defp generate_actor_specs do
    repo_sketcher = %{uuid: "repo_sketcher", name: "RepoSketcher", role: "RepoSketcher"}
    file_sketchers = for i <- 1..3, do: %{uuid: "file_sketcher_#{i}", name: "FileSketcher_#{i}", role: "FileSketcher"}
    sketch_fillers = for i <- 1..3, do: %{uuid: "sketch_filler_#{i}", name: "SketchFiller_#{i}", role: "SketchFiller"}

    [repo_sketcher | file_sketchers ++ sketch_fillers]
  end

  defp connect_actors(from_pid, to_pid, to_uuid, actor_specs) do
    to_role = get_role(to_uuid, actor_specs)
    message = %Message{
      sender: "",
      receiver: "",
      content: "original message",
      parameters: %{
        "to_uuid" => to_uuid,
        "to_pid" => to_pid,
        "to_role" => to_role
      },
      timestamp: :os.system_time(:millisecond),
      uuid: UUID.uuid4()
    }
    GenServer.cast(from_pid, {:explore, message})
  end

  defp get_role(uuid, actor_specs) do
    actor_specs
    |> Enum.find(fn actor_spec -> actor_spec.uuid == uuid end)
    |> Map.get(:role)
  end
end
