defmodule Actor do
  use GenServer

  def start_link(args) do
    GenServer.start_link(__MODULE__, args, uid: args["uid"])
  end

  def init(args) do
    try do
      # 启动一个 Python 解释器的实例 并记录其 PID
      python_session = Python.start(args["env"])
      # 将 当前 GenServer 进程注册为 Python 代码中异步操作的回调处理器
      Python.call(python_session, String.to_atom(args["env"]), :register_handler, [self()])
      state = %{
        uid: uid
        name: name,
        role: role,
        # uid: content
        input_cache: %{},
        compute_result: [],
        # uid: message
        output_cache: %{},
        prefix: [],
        # uid: pid
        next: %{},
      }
    rescue
      e in UndefinedFunctionError ->
        IO.puts("An error occurred: #{inspect(e)}")
        {:stop, e}
    end
  end

  def process_input(state) do
    prefix = state.prefix
    input_cache = state.input_cache

    # 检查所有入度消息是否已经到达
    all_received = Enum.all?(prefix, fn uid ->
      Map.has_key?(input_cache, uid)
    end)

    # 所有入度消息已到达
    if all_received do
      # 打包入度消息
      input = construct_input(state)
      compute(input, state)
  end

  def construct_input(state) do

  end

  def handle_cast({:receive, message}, state) do
    from_uid = message["uid"]
    content = message["content"]

    new_input_cache = Map.put(state.input_cache, uid, content)
    new_state = %{state | input_cache: new_input_cache}

    process_input(new_state)

    {:noreply, new_state}
  end



end
