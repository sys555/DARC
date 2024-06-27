defmodule PythonPortExample do
  def run do
    {:ok, pid_alice_producer} = Ain.ActorModelServer.start_link(%{
      "init" => "alice_producer",
      "env" => "Producer",
    })
    {:ok, pid_bob_consumer} = Ain.ActorModelServer.start_link(%{
      "init" => "bob_consumer",
      "env" => "Consumer",
    })

    GenServer.cast(pid_alice_producer, {:receive, "bob_consumer ASK alice_producer", pid_bob_consumer, :initial})
    # GenServer.cast(pid_bob_consumer, {:receive, "alice_producer ASK bob_consumer", pid_alice_producer, :initial})
  end

end
