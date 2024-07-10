defmodule DB.Task do
  use Ecto.Schema

  @primary_key {:uid, Ecto.UUID, autogenerate: true}
  schema "tasks" do
    field :uid, Ecto.UUID
    field :ttl, :integer
    field :nodes, :map
    field :input, :map
    field :output, :map
    field :diff_graph, :map
    field :whole_graph, :map
    field :logs, :map

    timestamps()
  end

end
