defmodule Ain.Bridge do
  alias Util.{DBUtil, ActorUtil}
  alias DB.Repo

  def load(graph_id) do
    # load with graph_id
    Repo.start_link()
    actor_specs = DBUtil.generate_actor_specs_from_db(graph_id)
    {:ok, _supervisor} = Ain.ActorSupervisor.start_link(actor_specs)
    edges = DBUtil.get_edges_by_graph_id(graph_id)
    # IO.inspect(edges)
    # IO.inspect(actor_specs)
    ActorUtil.connect_actors(edges, actor_specs)
  end

  def send(actor_uuid, message) do
    Repo.start_link()
    # message = %Message{
    #   sender: self(),
    #   receiver: self(),
    #   content: "hi",
    #   parameters: %{},
    #   timestamp: :os.system_time(:millisecond),
    #   uuid: UUID.uuid4(),
    #   parameters: %{
    #     "from_role": ""
    #   },
    # }

    # graph_id = "36f9144c-e071-4e6f-a6fa-e020eca699c3"
    # actor_specs = DBUtil.generate_actor_specs_from_db(graph_id)
    # actor_desc = Enum.find(actor_specs, fn %{role: role} -> role == "QA" end)
    # IO.inspect(actor_desc)
    # GenServer.cast(:global.whereis_name(actor_desc.uuid), {:receive, message})
    actor_uuid = ""
    message = ""
  end
end
