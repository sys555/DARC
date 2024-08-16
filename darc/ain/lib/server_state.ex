defmodule MasrpcServerState do
  use GenServer

  def start_link(initial_state \\ %{}) do
    GenServer.start_link(__MODULE__, initial_state, name: __MODULE__)
  end

  def init(initial_state) do
    args = %{uid: "default_uid"}
    {:ok, mas_pid} = MAS.start_link(args)
    {:ok, %{:mas_pid => mas_pid}}
  end

  def handle_call(:get_mas_pid, _from, state) do
    {:reply, Map.get(state, :mas_pid), state}
  end

  def get_mas_pid do
    GenServer.call(__MODULE__, :get_mas_pid)
  end
end
