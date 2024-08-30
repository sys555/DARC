defmodule MASTest do
  use ExUnit.Case, async: false
  alias MAS
  alias MockDataHelper
  alias Util.{DBUtil, ActorUtil}
  alias Ain.Actor

  setup_all do
    :ok = Ecto.Adapters.SQL.Sandbox.checkout(DB.Repo)
    Ecto.Adapters.SQL.Sandbox.mode(DB.Repo, {:shared, self()})

    mock_data = MockDataHelper.generate_mock_data()
    MockDataHelper.insert_mock_data(mock_data)

    uid = "test_uid"
    {:ok, pid} = MAS.start_link(%{uid: uid})
    :timer.sleep(1_000)

    {:ok, pid: pid, mock_data: mock_data}
  end

  @tag :skip
  test "handles :load call and initializes actors", %{pid: pid, mock_data: mock_data} do
    graph_id = List.first(mock_data.actors)[:graph_id]
    :ok = GenServer.cast(pid, {:load, graph_id, self()})

    receive do
      {:load_complete, ^graph_id} ->
        for actor <- mock_data.actors do
          actor_pid = :global.whereis_name(actor[:uid])
          assert Process.alive?(actor_pid)
        end
    after
      24_000 ->
        flunk("Did not receive :load_complete message in time")
    end
  end

  @tag :skip
  test "handles :send call and sends message to the target actor", %{pid: pid, mock_data: mock_data} do
    # wait :load
    :timer.sleep(24_000)

    actor = List.first(mock_data.actors)
    target_uid = actor[:uid]

    actor_pid = :global.whereis_name(actor[:uid])
    assert Process.alive?(actor_pid)

    message_content = "Hello, World!"
    :ok = GenServer.cast(pid, {:send, target_uid, %{"content": message_content}})
    :timer.sleep(1_000)
    target_state = :sys.get_state(actor_pid)
    mas_state = :sys.get_state(pid)

    refute Enum.empty?(target_state.logs)

    actor_2 = Enum.at(mock_data.actors, 1)
    target_uid = actor[:uid]
    :ok = GenServer.cast(pid, {:get_log, target_uid, self()})

    receive do
      {:get_log_complete, matching_logs} ->
        assert Enum.all?(matching_logs, fn message ->
          message.receiver_uid == target_uid
        end)
    after 2_000 ->
      flunk("Did not receive :get_log_complete message in time")
    end
  end

  @tag :skip
  test "handles :update_agent call and updates the agent state", %{pid: pid, mock_data: mock_data} do
    graph_id = List.first(mock_data.actors)[:graph_id]
    :ok = GenServer.cast(pid, {:load, graph_id, self()})

    :timer.sleep(15_000)

    actor = List.first(mock_data.actors)
    target_uid = actor[:uid]
    actor_pid = :global.whereis_name(target_uid)
    assert Process.alive?(actor_pid)

    updated_args = %{
      uid: target_uid,
      name: "John Doe",
      role: "Speaker",
      age: 30,
      graph_id: Ecto.UUID.generate()
    }

    # Assuming update_actor/2 is a function in your module
    case DBUtil.update_actor(target_uid, updated_args) do
      {:ok, _updated_actor} -> :ok
      {:error, reason} -> flunk("Failed to update actor: #{reason}")
    end
    :timer.sleep(1_000)
    actor = DBUtil.get_actor_with_uid(target_uid)
    GenServer.cast(pid, {:update_actor, target_uid})
    # Wait for state to update
    :timer.sleep(1_000)
    new_state = :sys.get_state(actor_pid)
    # IO.inspect(new_state)
    assert new_state.uid == target_uid
    assert new_state.name == "John Doe"
    assert new_state.role == "Speaker"
  end

  test "handle_cast with {:new_edge, edge_uid} when edge exists", %{pid: pid, mock_data: mock_data} do
    graph_id = List.first(mock_data.actors)[:graph_id]
    :ok = GenServer.cast(pid, {:load, graph_id, self()})

    :timer.sleep(5_000)

    [edge1, edge2 | _] = mock_data.edges
    :timer.sleep(1_000)
    actor_pid = :global.whereis_name(edge1.from_uid)
    IO.inspect(Actor.get_state(actor_pid))
    IO.inspect(edge1)
    GenServer.cast(pid, {:del_edge, edge1})
    :timer.sleep(5_000)
    IO.inspect(Actor.get_state(actor_pid))
  end
end
