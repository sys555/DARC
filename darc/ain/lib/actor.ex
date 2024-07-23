defmodule Ain.Actor do
  use GenServer
  alias Ain.Python

  def start_link(args) do
    GenServer.start_link(__MODULE__, args, uuid: args.uuid)
  end

  def init(args) do
    try do
      # 启动一个 Python 解释器的实例 并记录其 PID
      python_session = Python.start(args.role)
      # 将 当前 GenServer 进程注册为 Python 代码中异步操作的回调处理器
      Python.call(python_session, String.to_atom(args.role), :register_handler, [self()])
      state = %{
        uuid: "",
        name: "",
        role: args.role,
        # address(uuid) => pid
        address_book: args.address_book,
        # address(uuid) => role
        face: args.face,
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
    uuid = parsed_message.uuid
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
    updated_logs = [message | state.logs]
    updated_state = %{state | logs: updated_logs}

    computed_messages = compute(state, message)

    computed_messages
    |> Enum.each(fn computed_message ->
      {to_pid, response_message} = parse_computed_message(computed_message, state)
      GenServer.cast(to_pid, {:receive, response_message})
    end)

    {:noreply, updated_state}
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
    role = computed_message["parameters"]["to_role"]
    uuids = state.face
            |> Enum.filter(fn {_, r} -> r == role end)
            |> Enum.map(fn {uuid, _} -> uuid end)

    pids = uuids |> Enum.map(&Map.get(state.address_book, &1))

    if pids == [] do
      raise EmptyPidsError
    end

    to_pid = path(pids)
    message = Message.create(
      self(),
      to_pid,
      computed_message["content"],
      %{}
    )
    {to_pid, message}
  end

  defp path(pids) do
    # random
    Enum.random(pids)
  end

end
