defmodule DAGContract do
  use GenServer

  # 初始化合约
  def start_link(_) do
    GenServer.start_link(__MODULE__, %{})
  end

  def init(_) do
    # 初始化状态，包括节点信息、边的信息、消息计数器
    {:ok, %{nodes: %{}, edges: %{}, counter: %{}}}
  end

  # 添加已经存在的节点
  def add_node(contract_pid, name, pid) do
    GenServer.cast(contract_pid, {:add_node, name, pid})
  end

  # 添加边
  def add_edge(contract_pid, from, to) do
    GenServer.cast(contract_pid, {:add_edge, from, to})
  end

  # 发送消息到指定节点
  def send_message(contract_pid, node, message) do
    GenServer.cast(contract_pid, {:send_message, node, message})
  end

  # 处理添加节点，现在需要处理节点的 PID
  def handle_cast({:add_node, name, pid}, state) do
    # 计数器初始化为 0
    # 计数器用来跟踪需要从其他节点接收多少消息才能开始处理自己的消息
    new_counter = Map.put(state.counter, name, 0)
    # 更新 nodes
    updated_nodes = Map.put(state.nodes, name, %{pid: pid, message: nil})
    {:noreply, %{state | nodes: updated_nodes, counter: new_counter}}
  end

  # 处理添加边
  def handle_cast({:add_edge, from, to}, state) do
    updated_edges = Map.update(state.edges, from, [to], &[to | &1])
    updated_counter = Map.update(state.counter, to, 1, &(&1 + 1))
    {:noreply, %{state | edges: updated_edges, counter: updated_counter}}
  end

  # 处理发送消息
  def handle_cast({:send_message, node, message}, state) do
    manage_message_flow(node, message, state)
    {:noreply, state}
  end

  # 管理消息流
  defp manage_message_flow(node, message, state) do
    node_info = Map.fetch!(state.nodes, node)
    if can_process?(node, state) do
      send(node_info.pid, {:process_message, message})
      update_after_sending(node, state)
    end
  end

  # 检查节点是否可以处理消息
  defp can_process?(node, %{counter: counter}) do
    Map.get(counter, node, 0) == 0
  end

  # 更新发送后的状态
  defp update_after_sending(node, state) do
    Map.update!(state.counter, node, &(&1 - 1))
  end
end
