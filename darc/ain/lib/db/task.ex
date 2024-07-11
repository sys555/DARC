defmodule DB.Task do
  use Ecto.Schema
  import Ecto.Changeset

  @primary_key {:uid, :binary_id, autogenerate: true}
  schema "tasks" do
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
