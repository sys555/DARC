defmodule MAS do
  use GenServer
  alias DB.Repo
  alias DB.Factory
  alias DB.{Actor, Edge, Task}
  alias Util.{DBUtil, ActorUtil}

  def start_link(args) do
    GenServer.start_link(__MODULE__, args, name: {:global, args.uid})
  end

  def init(args) do
    try do
      state = %{
        uid: Map.get(args, :uid, ""),
        logs: [],
      }
      Repo.start_link()
      {:ok, state}
    rescue
      e in UndefinedFunctionError ->
        IO.puts("An error occurred in mas init: #{inspect(e)}")
        {:stop, e}
    end
  end

  def handle_cast({:load, graph_id, caller_pid}, state) do
    # query
    actor_specs = DBUtil.generate_actor_specs_from_db(graph_id)
    updated_actor_specs = Enum.map(actor_specs, fn actor_spec ->
      Map.put(actor_spec, :logger, self())
    end)
    {:ok, _supervisor} = Ain.ActorSupervisor.start_link(updated_actor_specs)
    # query
    edges = DBUtil.get_edges_by_graph_id(graph_id)
    ActorUtil.connect_actors(edges, actor_specs)
    IO.inspect(actor_specs)
    # 发送完成消息给调用进程
    send(caller_pid, {:load_complete, graph_id})

    {:noreply, state}
  end

  def handle_cast({:send, uid, message}, state) do
    message = %Message{
              content: Map.get(message, "content", ""),
              parameters: Map.get(message, "parameters", %{}),
            }
    IO.inspect(message)

    case :global.whereis_name(uid) do
      :undefined ->
        IO.puts("No process found for UID: #{uid}")
        {:noreply, state}
      pid ->
        GenServer.cast(pid, {:receive, message})
        {:noreply, state}
    end
  end

  def handle_call(_msg, _from, state) do
    {:reply, {:error, :unknown_message}, state}
  end

  def handle_cast({:log, message}, state) do
    new_logs = [message | state.logs]
    new_state = %{state | logs: new_logs}
    {:noreply, new_state}
  end

  def handle_cast({:get_log, uid, caller_pid}, state) do
    IO.inspect(state.logs)
    matching_logs = Enum.filter(state.logs, fn message ->
      message.receiver_uid == uid
    end)

    send(caller_pid, {:get_log_complete, matching_logs})
    {:noreply, state}
  end

  def handle_cast({:update_actor, uid}, state) do
    case DBUtil.get_actor_with_uid(uid) do
      nil ->
        {:noreply, state}
      actor ->
        GenServer.cast(:global.whereis_name(uid), {:update_actor, actor})
        {:noreply, state}
    end
  end

  def handle_cast({:new_edge, edge}, state) do
    case DBUtil.get_edge_with_uid(edge.uid) do
      nil ->
        {:noreply, state}
      edge ->
        case DBUtil.get_actor_with_uid(edge.to_uid) do
          nil ->
            {:noreply, state}
          to_actor ->
            to_actor = DBUtil.get_actor_with_uid(edge.to_uid)
            to_role = to_actor.role
            to_uid = edge.to_uid
            to_pid = :global.whereis_name(edge.to_uid)
            message = %Message{
              content: "hi",
              parameters: %{
                "to_uid" => to_uid,
                "to_pid" => to_pid,
                "to_role" => to_role
              },
            }
            GenServer.cast(:global.whereis_name(edge.from_uid), {:explore, message})
            {:noreply, state}
        end
    end
  end

  def handle_cast({:del_edge, edge}, state) do
    case DBUtil.get_actor_with_uid(edge.to_uid) do
      nil ->
        {:noreply, state}
      to_actor ->
        to_actor = DBUtil.get_actor_with_uid(edge.to_uid)
        to_role = to_actor.role
        to_uid = edge.to_uid
        to_pid = :global.whereis_name(edge.to_uid)
        message = %Message{
          content: "hi",
          parameters: %{
            "to_uid" => to_uid,
            "to_pid" => to_pid,
            "to_role" => to_role
          },
        }

        GenServer.cast(:global.whereis_name(edge.from_uid), {:parting, message})
        {:noreply, state}
    end
  end
end
