defmodule MASTest do
  use ExUnit.Case, async: false
  alias MAS
  alias MockDataHelper

  setup_all do
    :ok = Ecto.Adapters.SQL.Sandbox.checkout(DB.Repo)
    Ecto.Adapters.SQL.Sandbox.mode(DB.Repo, {:shared, self()})

    mock_data = MockDataHelper.generate_mock_data()
    MockDataHelper.insert_mock_data(mock_data)

    uid = "test_uid"
    {:ok, pid} = MAS.start_link(%{uid: uid})

    {:ok, pid: pid, mock_data: mock_data}
  end

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

  test "handles :send call and sends message to the target actor", %{pid: pid, mock_data: mock_data} do
    # wait :load
    :timer.sleep(24_000)

    actor = List.first(mock_data.actors)
    target_uid = actor[:uid]

    actor_pid = :global.whereis_name(actor[:uid])
    assert Process.alive?(actor_pid)

    message_content = "Hello, World!"
    :ok = GenServer.call(pid, {:send, target_uid, message_content})
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
end
