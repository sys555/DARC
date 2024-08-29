defmodule Ain.Actor do
  use GenServer
  alias Ain.Python
  alias Util.ActorUtil
  alias DB.{Actor, Edge, Task}

  def start_link(args) do
    GenServer.start_link(__MODULE__, args, name: {:global, args.uid})
  end

  def init(args) do
    try do
      # 启动一个 Python 解释器的实例 并记录其 PID
      python_session = Python.start(args.role)
      # 将 当前 GenServer 进程注册为 Python 代码中异步操作的回调处理器
      Python.call(python_session, String.to_atom(args.role), :register_handler, [self()])
      state = %{
        uid: Map.get(args, :uid, ""),
        name: Map.get(args, :name, ""),
        role: Map.get(args, :role, ""),
        # address(uid) => pid
        address_book: Map.get(args, :address_book, %{}),
        # address(uid) => role
        face: Map.get(args, :face, %{}),
        logs: [],
        python_session: python_session,
        logger: Map.get(args, :logger, nil),
      }
      {:ok, state}
    rescue
      e in UndefinedFunctionError ->
        IO.puts("An error occurred in actor init: #{inspect(e)}")
        {:stop, e}
    end
  end

  def handle_cast({:explore, message}, state) do
    parsed_message = Message.parse(message)
    uid = parsed_message.parameters["to_uid"]
    to_pid = parsed_message.parameters["to_pid"]
    to_role = parsed_message.parameters["to_role"]
    new_address_book = Map.put(state.address_book, uid, to_pid)
    new_face = Map.put(state.face, uid, to_role)
    new_state = %{
      state
      | address_book: new_address_book,
        face: new_face,
    }
    {:noreply, new_state}
  end

  def handle_cast({:receive, message}, state) do
    # IO.inspect("================================================================================================================================")
    # IO.inspect(state)
    # IO.inspect("================================================================================================================================")
    try do
      updated_logs = [message | state.logs]
      updated_state = %{state | logs: updated_logs}
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
              GenServer.cast(state.logger, {:log, response_message})
            else
              # IO.puts("Parsed message returned nil values, skipping cast.")
            end
          rescue
            e in Enum.EmptyError ->
              IO.inspect(state)
              IO.puts("An error occurred in handle_cast(:receive) Enum.EmptyError : #{inspect(e)}")
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
          uids when uids != [] <- fetch_uids(role, state.face),
          pids when pids != [] <- fetch_pids(uids, state.address_book),
          to_pid when not is_nil(to_pid) <- path(pids) do
            content = Map.get(computed_message, "content", "")
            message = %Message{
              uid: UUID.uuid4(),
              sender_pid: self(),
              receiver_pid: to_pid,
              sender_uid: state.uid,
              receiver_uid: ActorUtil.get_uid_by_pid(state.address_book, to_pid),
              content: content,
              parameters: computed_message["parameters"],
              timestamp: DateTime.utc_now() |> DateTime.to_iso8601(),
            }
      {to_pid, message}
    else
      %{} ->
        # IO.puts(state.uid)
        # IO.puts(state.name)
        # IO.puts(state.role)
        # IO.puts("Info: computed_message is empty or to_role is missing.")
        {"None", "None"}
      uids when uids == [] ->
        # IO.puts("Info: No UIDs found for role #{computed_message["parameters"]["to_role"]}.")
        {"None", "None"}
      pids when pids == [] ->
        # IO.puts("Infp: No PIDs found for the given UIDs.")
        {"None", "None"}
      to_pid when is_nil(to_pid) ->
        # IO.puts("Info: path(pids) returned nil.")
        {"None", "None"}
    end
  end

  def handle_cast({:update_actor, actor}, state) do
    # 更新已有的键
    new_state = %{
      state
      | uid: actor.uid || state.uid,
        name: actor.name || state.name,
        role: actor.role || state.role
    }

    python_session = Python.start(actor.role)
    Python.call(python_session, String.to_atom(actor.role), :register_handler, [self()])

    new_state = %{
      new_state
      | python_session: python_session,
    }
    {:noreply, new_state}
  end

  defp fetch_uids(role, face) do
    if role == "random" do
      face
      |> Enum.map(fn {uid, _} -> uid end)
      |> Enum.random()
      |> List.wrap()
    else
      face
      |> Enum.filter(fn {_, r} -> r == role end)
      |> Enum.map(fn {uid, _} -> uid end)
    end
  end

  defp fetch_pids(uids, address_book) do
    uids |> Enum.map(&Map.get(address_book, &1))
  end

  defp path(pids) do
    # random
    Enum.random(pids)
  end

end
