defmodule ReadmeContract do
  def start_link(initial_state \\ %{}) do
    GenServer.start_link(__MODULE__, initial_state)
  end

  def init(initial_state) do
    state = %{
      readme_content: initial_state[:readme],
      repository_sketch: "",
      repo_sketcher_pid: nil,
      file_list: [],
      # pid => file_path
      file_sketcher_pid_map: %{},
      # file_path => file_sketch
      file_sketch_map: %{},
      # pid => file_path
      sketch_filler_pid_map: %{},
      # file_path => function_body
      function_body_map: %{},
      # node_name => pid
      address_book: %{},
    }

    {:ok, state}
  end

  def start(readme_content) do
    initial_state = %{
      readme: readme_content,
    }
    {:ok, pid} = start_link(initial_state)
    GenServer.cast(pid, {:repo_sketch_start})
    pid
  end

  def handle_cast({:repo_sketch_start}, state) do
    node_name = "repo_sketcher"
    env = "RepoSketcher"
    logs = []

    case Ain.ActorModelServer.start_link(%{"init" => node_name, "env" => env, "logs" => logs}) do
      {:ok, repo_sketcher_pid} ->
        new_state = %{
          state
          | repo_sketcher_pid: repo_sketcher_pid,
            address_book: Map.put(state.address_book, node_name, repo_sketcher_pid)
        }
        message = state.readme_content
        GenServer.cast(repo_sketcher_pid, {:receive, message, self(), :initial})
        {:noreply, new_state}

      {:error, _reason} ->
        {:stop, :failed_to_start_repo_sketcher, state}
    end
  end

  def handle_cast({:sketch_filler_pid_map, sketch_filler_output, from_pid}, state) do
    ## update state["sketch_filler_map"] with file_sketcher_output, from_pid
  end

  def handle_cast({:receive, message, from_pid, :ack}, state) do
    new_state =
      cond do
        from_pid == state.repo_sketcher_pid ->
          {:noreply, new_state} = handle_repo_sketcher_message(message, state)
          new_state

        Map.has_key?(state.file_sketcher_pid_map, from_pid) ->
          {:noreply, new_state} = handle_file_sketcher_message(message, from_pid, state)
          new_state

        Map.has_key?(state.sketch_filler_pid_map, from_pid) ->
          {:noreply, new_state} = handle_sketch_filler_message(message, from_pid, state)
          new_state

        true ->
          state
      end
    {:noreply, new_state}
  end

  defp handle_repo_sketcher_message(repo_sketcher_output, state) do
    ## update state["repository_sketch"] with repo_sketcher_output
    ## repo_sketcher_output => file_list
    ## spawn a [list] of file_sketcher
    ## update state["file_sketcher_pid_map"]
    ## cast message to file_sketcher
    {_, file_list} = parse_repo_sketcher_output(repo_sketcher_output)
    {file_sketcher_pid_map, address_book} = spawn_file_sketchers(file_list, self(), state.address_book)

    new_state = %{
      state
      | repository_sketch: repo_sketcher_output,
        file_list: file_list,
        file_sketcher_pid_map: file_sketcher_pid_map,
        address_book: address_book
    }

    Enum.each(file_sketcher_pid_map, fn {pid, file_path} ->
      data = %{
        readme_content: new_state.readme_content,
        repository_sketch: new_state.repository_sketch,
        file_path: file_path
      }
      message = Jason.encode!(data)
      GenServer.cast(pid, {:receive, message, self(), :initial})
    end)

    {:noreply, new_state}
  end

  defp handle_file_sketcher_message(file_sketcher_output, from_pid, state) do
    ## update state["file_sketch_map"] with file_sketcher_output, from_pid
    ## spawn a sketch_filler
    ## update state["sketch_filler_pid_map"]
    ## cast meesage to sketch_filler
    ## update state[""]
    file_path = state.file_sketcher_pid_map[from_pid]
    new_file_sketch_map = Map.put(state.file_sketch_map, file_path, file_sketcher_output)
    node_name = "sketch_filler#{file_path}"
    env = "SketchFiller"
    logs = []

    case Ain.ActorModelServer.start_link(%{"init" => node_name, "env" => env, "logs" => logs}) do
      {:ok, sketch_filler_pid} ->
        # update state
        new_sketch_filler_pid_map = Map.put(state.sketch_filler_pid_map, sketch_filler_pid, file_path)
        new_address_book = Map.put(state.address_book, node_name, sketch_filler_pid)

        new_state = %{
          state
          | file_sketch_map: new_file_sketch_map,
            sketch_filler_pid_map: new_sketch_filler_pid_map,
            address_book: new_address_book
        }

        # call filler
        data = %{
          readme_content: state.readme_content,
          repository_sketch: state.repository_sketch,
          file_sketches: file_sketcher_output
        }
        message = Jason.encode!(data)
        GenServer.cast(sketch_filler_pid, {:receive, message, self(), :initial})

        {:noreply, new_state}
      {:error, _reason} ->
        {:stop, :failed_to_start_sketch_filler, state}
    end
  end

  defp handle_sketch_filler_message(sketch_filler_output, from_pid, state) do
    file_path = state.sketch_filler_pid_map[from_pid]
    new_function_body_map = Map.put(state.function_body_map, file_path, sketch_filler_output)

    new_state = %{
      state
      | function_body_map: new_function_body_map
    }

  # Check if all values are filled
  if Enum.count(new_state.function_body_map) == Enum.count(new_state.file_list) do
    # Schedule a call to get_logs/1
    Process.send_after(self(), :get_logs, 0)
  end

    {:noreply, new_state}
  end

  defp parse_repo_sketcher_output(repo_sketcher_output) do
    case Jason.decode(repo_sketcher_output) do
      {:ok, %{"parsed_response" => parsed_response, "repo_sketch_paths" => repo_sketch_paths}} ->
        {:ok, repo_sketch_paths}
      {:error, reason} ->
        IO.puts("Failed to parse JSON: #{reason}")
    end
  end

  defp spawn_file_sketchers(file_list, parent, address_book) do
    Enum.reduce(file_list, {%{}, address_book}, fn file_path, {acc, address_book} ->
      node_name = "file_sketcher_#{file_path}"
      env = "FileSketcher"
      logs = []

      case Ain.ActorModelServer.start_link(%{"init" => node_name, "env" => env, "logs" => logs}) do
        {:ok, file_sketcher_pid} ->
          new_acc = Map.put(acc, file_sketcher_pid, file_path)
          new_address_book = Map.put(address_book, node_name, file_sketcher_pid)
          {new_acc, new_address_book}

        {:error, _reason} ->
          {acc, address_book}
      end
    end)
  end

  def handle_call(:get_logs, _from, state) do
    # 获取当前UTC时间
    timestamp = DateTime.utc_now() |> DateTime.to_string()

    # 格式化 repository_sketch，确保多行字符串正确处理
    formatted_repository_sketch = String.replace(state.repository_sketch, "\n", "\n    ")

    # 格式化 file_sketch_map，确保每个文件内容在正确的代码块中
    formatted_file_sketch_map = state.file_sketch_map
    |> Enum.map(fn {key, value} ->
      ext = Path.extname(key) |> String.trim_leading(".")
      {key, "```#{ext}\n#{value}\n```"}
    end)
    |> Enum.into(%{})
    IO.inspect(state.repository_sketch)
    IO.inspect(state.file_sketch_map)
    log_content = """
    Log Timestamp: #{timestamp}

    Repository Sketch:
      #{formatted_repository_sketch}

    File Sketch Map:
    #{inspect(formatted_file_sketch_map, pretty: true)}

    Function Body Map:
    #{inspect(state.function_body_map, pretty: true)}
    """

    # 将内容写入日志文件
    File.write!("readme_contract.log", log_content)

    {:reply, :ok, state}
  end

  def get_logs(pid) do
    GenServer.call(pid, :get_logs)
  end

end
