defmodule Ain.Actor do
  use GenServer
  alias Ain.Python

  def start_link(args) do
    GenServer.start_link(__MODULE__, args, name: {:global, args.uuid})
  end

  def init(args) do
    try do
      # 启动一个 Python 解释器的实例 并记录其 PID
      python_session = Python.start(args.role)
      # 将 当前 GenServer 进程注册为 Python 代码中异步操作的回调处理器
      Python.call(python_session, String.to_atom(args.role), :register_handler, [self()])
      state = %{
        uuid: Map.get(args, :uuid, ""),
        name: Map.get(args, :name, ""),
        role: Map.get(args, :role, ""),
        # address(uuid) => pid
        address_book: Map.get(args, :address_book, %{}),
        # address(uuid) => role
        face: Map.get(args, :face, %{}),
        logs: [],
        python_session: python_session,
      }
      {:ok, state}
    rescue
      e in UndefinedFunctionError ->
        IO.puts("An error occurred: #{inspect(e)}")
        {:stop, e}
    end
  end

  def handle_cast({:explore, message}, state) do
    parsed_message = Message.parse(message)
    uuid = parsed_message.parameters["to_uuid"]
    to_pid = parsed_message.parameters["to_pid"]
    to_role = parsed_message.parameters["to_role"]
    new_address_book = Map.put(state.address_book, uuid, to_pid)
    new_face = Map.put(state.face, uuid, to_role)
    new_state = %{
      state
      | address_book: new_address_book,
        face: new_face,
    }
    {:noreply, new_state}
  end

  def handle_cast({:receive, message}, state) do
    IO.inspect("================================================================================================================================")
    IO.inspect(state)
    IO.inspect("================================================================================================================================")
    try do
      updated_logs = [message | state.logs]
      updated_state = %{state | logs: updated_logs}
      IO.inspect(message)
      trimmed_message = %{
        content: message.content,
        parameters: message.parameters
      }
      json = Jason.encode!(trimmed_message)

      computed_messages = compute(state, json)

      if Enum.empty?(computed_messages) do
        IO.puts("Computed messages are empty, nothing to process.")
      else
        Enum.each(computed_messages, fn computed_message ->
          try do
            {to_pid, response_message} = parse_computed_message(computed_message, state)
            if to_pid != "None" and response_message != "None" do
              GenServer.cast(to_pid, {:receive, response_message})
            else
              IO.puts("Parsed message returned nil values, skipping cast.")
            end
          rescue
            e in Enum.EmptyError ->
              IO.puts("An error occurred: #{inspect(e)}")
              # 记录日志或采取其他适当的操作
          end
        end)
      end

      {:noreply, updated_state}
    rescue
      e ->
        IO.puts("An error occurred in handle_cast(:receive): #{inspect(e)}")
        {:noreply, state}
    end
  end

  def compute(state, input) do
    python_call_res = Python.call(state.python_session, String.to_atom(state.role), :compute, [input])
    # 当传输或打印一个包含非 ASCII 字符的字符列表时，每个字符会被其对应的 Unicode 码点表示，必须做list to str
    res = List.to_string(python_call_res)
    Jason.decode!(res)
  end

  defmodule EmptyPidsError do
    defexception message: "No PIDs found for the specified role"
  end

  def parse_computed_message(computed_message, state) do
    with %{"parameters" => %{"to_role" => role}} <- computed_message,
          uuids when uuids != [] <- fetch_uuids(role, state.face),
          pids when pids != [] <- fetch_pids(uuids, state.address_book),
          to_pid when not is_nil(to_pid) <- path(pids) do
      message = Message.create(self(), to_pid, "", computed_message["parameters"])
      {to_pid, message}
    else
      %{} ->
        IO.puts("Info: computed_message is empty or to_role is missing.")
        {"None", "None"}
      uuids when uuids == [] ->
        IO.puts("Info: No UUIDs found for role #{computed_message["parameters"]["to_role"]}.")
        {"None", "None"}
      pids when pids == [] ->
        IO.puts("Infp: No PIDs found for the given UUIDs.")
        {"None", "None"}
      to_pid when is_nil(to_pid) ->
        IO.puts("Info: path(pids) returned nil.")
        {"None", "None"}
    end
  end

  defp fetch_uuids(role, face) do
    face
    |> Enum.filter(fn {_, r} -> r == role end)
    |> Enum.map(fn {uuid, _} -> uuid end)
  end

  defp fetch_pids(uuids, address_book) do
    uuids |> Enum.map(&Map.get(address_book, &1))
  end

  defp path(pids) do
    # random
    Enum.random(pids)
  end

end
