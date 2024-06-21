defmodule DAGExample do
  def run do
    # Start the DAGContract
    {:ok, contract_pid} = DAGContract.start_link([])

    # Define and start nodes
    {:ok, pid1} = Ain.ActorModelServer.start_link(%{"init" => "node1", "env" => "compute_prefix", "logs" => []})
    {:ok, pid2} = Ain.ActorModelServer.start_link(%{"init" => "node2", "env" => "compute_prefix", "logs" => []})
    {:ok, pid3} = Ain.ActorModelServer.start_link(%{"init" => "node3", "env" => "compute_prefix", "logs" => []})
    {:ok, pid4} = Ain.ActorModelServer.start_link(%{"init" => "node4", "env" => "compute_prefix", "logs" => []})
    {:ok, pid5} = Ain.ActorModelServer.start_link(%{"init" => "node5", "env" => "compute_prefix", "logs" => []})

    :timer.sleep(1000)

    # # Add nodes to DAGContract
    DAGContract.add_node(contract_pid, "node1", pid1)
    DAGContract.add_node(contract_pid, "node2", pid2)
    DAGContract.add_node(contract_pid, "node3", pid3)
    DAGContract.add_node(contract_pid, "node4", pid4)
    DAGContract.add_node(contract_pid, "node5", pid5)

    # Setup edges according to the DAG structure
    DAGContract.add_edge(contract_pid, "node1", "node3")
    DAGContract.add_edge(contract_pid, "node2", "node3")
    DAGContract.add_edge(contract_pid, "node3", "node4")
    DAGContract.add_edge(contract_pid, "node4", "node5")

    # Wait a moment to ensure all nodes and edges are properly configured
    :timer.sleep(1000)

    # Start the message flow from the entry nodes
    DAGContract.send_message(contract_pid, "node1", "Hello from Node 1")
    DAGContract.send_message(contract_pid, "node2", "Hello from Node 2")

    # # Simulate a wait to observe message propagation in the system
    # :timer.sleep(3000)

    # # Additional logic to inspect the final state or handle responses could be added here
    # IO.puts("Message propagation complete.")
  end
end
