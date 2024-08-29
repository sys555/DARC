defmodule Ain.ActorTest do
  use ExUnit.Case
  import ExUnit.CaptureLog
  alias Ain.Actor
  alias Message
  alias Ain.Actor.EmptyPidsError
  alias DB.Repo
  alias Util.{DBUtil, ActorUtil}
  import DB.{Actor, Edge, Task}

  setup do
    :ok = Ecto.Adapters.SQL.Sandbox.checkout(DB.Repo)
    state = %{
      face: %{"uuid1" => "role1", "uuid2" => "role1", "uuid3" => "role2"},
      address_book: %{"uuid1" => self(), "uuid2" => self(), "uuid3" => self()},
      logs: [],
      python_session: "",
      role: "Speaker"
    }
    {:ok, state: state}
  end

  @tag :skip
  test "parse_computed_message/1 creates a message with the correct fields", %{state: state} do
    computed_message = %{
      "sender" => "sender",
      "receiver" => "receiver",
      "content" => "content",
      "parameters" => %{"to_role" => "role1"}
    }

    {to_pid, message} = Actor.parse_computed_message(computed_message, state)

    assert to_pid == self()
    assert message.sender == self()
    assert message.receiver == self()
    assert message.content == "content"
    assert message.parameters == %{}
    assert message.timestamp != nil
    assert message.uid != nil
  end

  @tag :skip
  test "parse_computed_message/1 raises EmptyPidsError when no PIDs are found for the role", %{state: state} do
    computed_message = %{
      "sender" => "sender",
      "receiver" => "receiver",
      "content" => "content",
      "parameters" => %{"to_role" => "non_existing_role"}
    }

    assert_raise EmptyPidsError, fn ->
      Actor.parse_computed_message(computed_message, state)
    end
  end

  @tag :skip
  test "handle_cast/2 processes {:receive, message}", %{state: state} do
    message = %Message{
      sender_pid: self(),
      receiver_pid: self(),
      content: "original message",
      parameters: %{},
      timestamp: :os.system_time(:millisecond),
      uid: UUID.uuid4()
    }

    {:ok, pid} = GenServer.start_link(Actor, state)

    explored_message = %Message{
      uid: "uuid4",
      sender_pid: pid,
      receiver_pid: pid,
      content: nil,
      parameters: %{"to_pid" => pid, "to_role" => "role3"},
      timestamp: nil
    }

    GenServer.cast(pid, {:explore, explored_message})

    capture_log fn ->
      GenServer.cast(pid, {:receive, message})
    end

    :timer.sleep(1_000)
    # 检查状态
    new_state = :sys.get_state(pid)
    # 检查 logs 中是否包含预期的响应消息
    assert Enum.any?(new_state.logs, fn log -> log.content == "response 1" end)
    assert Enum.any?(new_state.logs, fn log -> log.content == "response 2" end)
  end


  @tag :skip
  test "handle_cast/2 processes {:explore, message} and updates state", %{state: state} do
    # Create the input message
    explored_message = %Message{
      uid: "uuid4",
      sender_pid: nil,
      receiver_pid: nil,
      content: nil,
      parameters: %{"to_pid" => self(), "to_role" => "role3"},
      timestamp: nil
    }

    {:ok, pid} = GenServer.start_link(Actor, state)

    # Send the explore message
    GenServer.cast(pid, {:explore, explored_message})

    :timer.sleep(100)

    # Fetch the updated state from the GenServer
    new_state = :sys.get_state(pid)

    assert new_state.address_book["uuid4"] == self()
    assert new_state.face["uuid4"] == "role3"
  end

  test "handle_cast/2 processes {:update_actor, actor}", %{state: state} do
    uid = Ecto.UUID.generate()
    actor_specs = [
      %{
        uid: uid,
        name: "John Doe",
        role: "Speaker",
        age: 30,
        graph_id: Ecto.UUID.generate()
      }
    ]

    # Insert the actor
    DBUtil.insert_actors(actor_specs)

    # Retrieve the actor using the `get_actor_with_uid/1` function
    actor = DBUtil.get_actor_with_uid(uid)
    IO.inspect(actor)
    {:ok, pid} = GenServer.start_link(Actor, state)
    :timer.sleep(1_000)
    GenServer.cast(pid, {:update_actor, actor})

    :timer.sleep(100)

    new_state = :sys.get_state(pid)

    assert new_state.uid == uid
    assert new_state.name == "John Doe"
    assert new_state.role == "Speaker"
  end
end
