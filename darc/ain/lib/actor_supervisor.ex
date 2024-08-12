defmodule Ain.ActorSupervisor do
  use Supervisor

  def start_link(actor_specs) do
    Supervisor.start_link(__MODULE__, actor_specs, name: __MODULE__)
  end

  def init(actor_specs) do
    children = Enum.map(actor_specs, fn actor_spec ->
      %{
        id: String.to_atom(Map.get(actor_spec, :uid, Ecto.UUID.generate())),
        start: {Ain.Actor, :start_link, [normalize_actor_spec(actor_spec)]}
      }
    end)

    Supervisor.init(children, strategy: :one_for_one)
  end

  defp normalize_actor_spec(actor_spec) do
    %{
      uid: Map.get(actor_spec, :uid, UUID.uuid4()),
      name: Map.get(actor_spec, :name, "Unknown"),
      role: Map.get(actor_spec, :role, "Unknown"),
      age: Map.get(actor_spec, :age, 0),
      graph_id: Map.get(actor_spec, :graph_id, nil),
      logger: Map.get(actor_spec, :logger, nil),
    }
  end
end
