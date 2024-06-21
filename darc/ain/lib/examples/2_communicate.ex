defmodule Communicate do
  def run do
    # 配置并启动第一个节点，节点名为 :node1
    {:ok, _pid1} = Ain.ActorModelServer.start_link(%{
      "init" => "node1",
      "env" => "compute_prefix",
      "logs" => ["Node1 log message 1", "Node1 log message 2"]
    })

    # 配置并启动第二个节点，节点名为 :node2
    {:ok, _pid2} = Ain.ActorModelServer.start_link(%{
      "init" => "node2",
      "env" => "compute_prefix",
      "logs" => ["Node2 log message 1", "Node2 log message 2"]
    })

    # 等待一小段时间确保两个节点都已启动并注册
    :timer.sleep(1000)

    # 从节点 :node1 发送日志到节点 :node2，并且包括消息内容
    initial_message = "Initial message from node1 to node2"
    Ain.ActorModelServer.send("node1", "node2", :initial, initial_message)

    # 等待足够时间以便节点 :node2 可以处理并响应消息
    :timer.sleep(1000)

    # 验证日志内容
    Ain.ActorModelServer.print_logs("node2")
  end
end
