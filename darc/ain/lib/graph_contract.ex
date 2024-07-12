defmodule GraphContract do
  use GenServer
  alias Util.GraphContractUtil

  def start_link(initial_state \\ %{}) do
    GenServer.start_link(__MODULE__, initial_state)
  end

  def init(initial_state) do
    # 初始化状态，包括节点信息、边的信息、每个节点的消息日志、节点的入度计数器
    state = %{
      # name => pid
      nodes: %{},
      # uid => {"env", "init"}
      nodes_info: initial_state[:nodes_info] || %{},
      edges: %{},
      edges_info: initial_state[:edges_info] || %{},
      task: initial_state[:task] || %{},
      logs: %{},
      queues: %{},
      counter: %{},
      init_data: initial_state[:init_data] || "",
    }

    {:ok, state}
  end

  # 暴露的初始化函数，接收 graph_id 和 init_data
  def start_with_graph_id_and_init_data(graph_id, init_data) do
    with {:ok, %{actors: nodes_info, edges: edges_info}} <- GraphContractUtil.get_graph_by_uid(graph_id) do

      initial_state = %{
        nodes_info: nodes_info,
        edges_info: edges_info,
        init_data: init_data,
      }

      {:ok, pid} = start_link(initial_state)
      run(initial_state, pid)
    else
      {:error, reason} -> {:error, reason}
    end
  end

  def run(state, contract_pid) do
    nodes = state.nodes_info
    edges = state.edges_info
    init_messages = state.init_data

    # 在映射中捕获可能的启动错误，并保留已有的PID或新的PID
    pids = Enum.reduce(nodes, %{}, fn {node_name, node_info}, acc ->
      env = Map.get(node_info, "env", "compute_prefix")
      logs = Map.get(node_info, "logs", [])
      IO.inspect(node_name)
      case Ain.ActorModelServer.start_link(%{"init" => node_name, "env" => env, "logs" => logs}) do
        {:ok, pid} ->
          Map.put(acc, node_name, pid)
        {:error, {:already_started, pid}} ->
          IO.puts("Node #{node_name} already started with PID #{inspect(pid)}")
          Map.put(acc, node_name, pid)
        _error ->
          acc
      end
    end)

    # 等待节点创建完毕
    :timer.sleep(1000)
    # node添加入graph
    Enum.each(pids, fn {node_name, pid} ->
      GenServer.cast(contract_pid, {:add_node, node_name, pid})
    end)

    # edge添加入graph
    Enum.each(edges, fn edge ->
      [from, to] = String.split(edge, ":")
      GenServer.cast(contract_pid, {:add_edge, from, to})
    end)

    # 等待节点与边添加完毕
    :timer.sleep(1000)

    entry_nodes = find_nodes_with_zero_indegree_and_nonzero_outdegree(nodes, edges)
    init_messages = generate_initial_messages(entry_nodes, state.init_data)
    # 发送初始消息
    GraphContract.init_messages(contract_pid, init_messages)
  end

  # 发送初始化消息到所有入度为0的节点，每个节点接收不同的消息
  # messages: %{"node1" => "Message for Node 1", "node2" => "Message for Node 2"}
  def init_messages(contract_pid, messages) do
    GenServer.cast(contract_pid, {:init_messages, messages})
  end

  def handle_cast({:add_node, name, pid}, state) do
    updated_state = %{
      state
      | nodes: Map.put(state.nodes, name, pid),
        logs: Map.put(state.logs, name, []),
        queues: Map.put(state.queues, name, []),
        counter: Map.put(state.counter, name, %{in_degree: [], out_degree: []})
    }

    {:noreply, updated_state}
  end

  def handle_cast({:add_edge, from, to}, state) do
    # 更新 edges 映射，将 'to' 节点加入 'from' 节点的出度列表中
    updated_edges = Map.update(state.edges, from, [to], fn existing_outs -> [to | existing_outs] end)
    # 更新计数器：增加 'to' 节点的入度计数
    updated_counter = Map.update!(state.counter, to, fn count ->
      %{count | in_degree: [from | count.in_degree]}
    end)
    # 更新 'from' 节点的出度信息
    updated_counter = Map.update!(updated_counter, from, fn count ->
      %{count | out_degree: [to | count.out_degree]}
    end)
    {:noreply, %{state | edges: updated_edges, counter: updated_counter}}
  end


  def handle_cast({:init_messages, messages}, state) do
    Enum.each(messages, fn {node, message} ->
      pid = Map.fetch!(state.nodes, node)
      in_degree = Map.get(state.counter, node, %{}).in_degree
      if length(in_degree) == 0 do
        GenServer.cast(pid, {:receive, message, self(), :initial})
      end
    end)
    {:noreply, state}
  end

  def handle_cast({:receive, message, from_pid, :ack}, state) do
    # IO.puts("Received ACK: #{message}")
    # write_with_timestamp("/Users/mac/Documents/pjlab/repo/LLMSafetyChallenge/darc/ain/lib/examples/logs.json", message)
    node = pid_to_node_name(from_pid, state)
    # 更新该节点的日志
    updated_logs = Map.update(state.logs, node, [message], fn existing_msgs -> [message | existing_msgs] end)

    # 根据 from_pid 的出度更新对应节点的队列
    from_node_out_degrees = Map.get(state.counter, node, %{}).out_degree
    updated_queues = Enum.reduce(from_node_out_degrees, state.queues, fn out_node, acc ->
      queue = Map.get(acc, out_node, [])
      new_queue = [message | queue]
      Map.put(acc, out_node, new_queue)
    end)

    # 检查更新后的队列，决定是否发送消息
    new_state = Enum.reduce(from_node_out_degrees, %{state | queues: updated_queues, logs: updated_logs}, fn out_node, acc ->
      queue = Map.get(acc.queues, out_node, [])
      in_degree_size = length(Map.get(acc.counter, out_node, %{}).in_degree)

      if length(queue) == in_degree_size do
        # 合并所有入度节点发送的消息并发送
        messages_to_send = Enum.join(queue, ", ")
        send_messages_to_node(state.nodes[out_node], messages_to_send)
        # 清空队列
        acc |> Map.update!(:queues, &Map.put(&1, out_node, []))
      else
        acc
      end
    end)

    {:noreply, new_state}
  end

  defp update_after_sending(node, message_reply, state) do
    # Update the state to indicate that the node has processed its message
    Map.update!(state.counter, node, &(%{&1 | processed: true}))
  end

  defp update_in_degree(counter, node) do
    Map.update(counter, node, %{in_degree: 1, out_degree: []}, fn entry ->
      %{entry | in_degree: entry.in_degree + 1}
    end)
  end

  defp pid_to_node_name(pid, state) do
    # IO.puts("Inspecting PID:")
    # IO.inspect(pid)

    # IO.puts("Inspecting State:")
    # IO.inspect(state)
    state.nodes
    |> Enum.find(fn {_key, val} -> val == pid end)
    |> case do
      nil -> nil
      {key, _val} -> key
    end
  end

  defp update_in_degree_queue(queues, node, message, counters) do
    current_queue = Map.get(queues, node, [])
    Map.put(queues, node, [message | current_queue])
  end

  defp send_messages_to_node(pid, message) do
    GenServer.cast(pid, {:receive, message, self(), :initial})
  end

  def get_logs(contract_pid) do
    GenServer.call(contract_pid, :get_logs)
  end

  def handle_call(:get_logs, _from, state) do
    {:reply, state.logs, state}
  end

  def run_setup(json_data, contract_pid) do
    nodes = Map.fetch!(json_data, "nodes")
    edges = Map.fetch!(json_data, "edges")
    init_messages = Map.fetch!(json_data, "data")

    # 在映射中捕获可能的启动错误，并保留已有的PID或新的PID
    pids = Enum.reduce(nodes, %{}, fn {node_name, node_info}, acc ->
      env = Map.get(node_info, "env", "compute_prefix")
      logs = Map.get(node_info, "logs", [])

      case Ain.ActorModelServer.start_link(%{"init" => node_name, "env" => env, "logs" => logs}) do
        {:ok, pid} ->
          Map.put(acc, node_name, pid)
        {:error, {:already_started, pid}} ->
          IO.puts("Node #{node_name} already started with PID #{inspect(pid)}")
          Map.put(acc, node_name, pid)
        _error ->
          acc
      end
    end)

    # 等待节点创建完毕
    :timer.sleep(1000)

    # node添加入graph
    Enum.each(pids, fn {node_name, pid} ->
      GenServer.cast(contract_pid, {:add_node, node_name, pid})
    end)

    # edge添加入graph
    Enum.each(edges, fn edge ->
      [from, to] = String.split(edge, ":")
      GenServer.cast(contract_pid, {:add_edge, from, to})
    end)

    # 等待节点与边添加完毕
    :timer.sleep(1000)

    # 发送初始消息
    GraphContract.init_messages(contract_pid, init_messages)
  end

  def write_with_timestamp(file_path, content) do
    # 获取当前时间并格式化
    timestamp = DateTime.utc_now() |> DateTime.to_string()

    # 要写入的内容，附带时间戳
    content_to_write = "#{content} - Timestamp: #{timestamp}\n"

    # 打开文件，模式为：追加模式，如果文件不存在则创建
    case File.open(file_path, [:append, :create]) do
      {:ok, file} ->
        # 写入内容并关闭文件
        IO.write(file, content_to_write)
        File.close(file)
        :ok

      {:error, reason} ->
        # 打印错误信息
        IO.puts("Error writing to file: #{reason}")
        {:error, reason}
    end
  end

  def find_nodes_with_zero_indegree_and_nonzero_outdegree(nodes, edges) do
    # 初始化入度和出度计数器
    initial_counter = Enum.reduce(Map.keys(nodes), %{}, fn node, acc ->
      Map.put(acc, node, %{in_degree: 0, out_degree: 0})
    end)

    # 更新入度和出度计数器
    counter = Enum.reduce(edges, initial_counter, fn edge, acc ->
      [from, to] = String.split(edge, ":")

      acc
      |> Map.update!(from, fn count -> %{count | out_degree: count.out_degree + 1} end)
      |> Map.update!(to, fn count -> %{count | in_degree: count.in_degree + 1} end)
    end)

    # 筛选入度为0且出度不为0的节点
    counter
    |> Enum.filter(fn {_node, counts} -> counts.in_degree == 0 and counts.out_degree > 0 end)
    |> Enum.map(fn {node, _counts} -> node end)
  end

  def generate_initial_messages(nodes_list, init_message) do
    Enum.reduce(nodes_list, %{}, fn node, acc ->
      Map.put(acc, node, init_message)
    end)
  end

end
