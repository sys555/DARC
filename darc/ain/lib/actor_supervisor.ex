defmodule Ain.ActorSupervisor do
  use Supervisor

  def start_link(actor_specs) do
    Supervisor.start_link(__MODULE__, actor_specs, name: __MODULE__)
  end

  def init(actor_specs) do
    children = Enum.map(actor_specs, fn %{uuid: uuid, name: name, role: role} ->
      %{
        id: String.to_atom(uuid),
        start: {Ain.Actor, :start_link, [%{uuid: uuid, name: name, role: role}]}
      }
    end)

    Supervisor.init(children, strategy: :one_for_one)
  end
end
