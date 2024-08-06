defmodule DB.Edge do
  use Ecto.Schema
  import Ecto.Changeset

  @primary_key {:uid, Ecto.UUID, autogenerate: true}
  schema "edge" do
    field :since, :integer, default: 0
    field :from_uid, Ecto.UUID
    field :to_uid, Ecto.UUID
    field :graph_id, :binary_id

    timestamps()
  end

  @doc """
  Creates a changeset for an edge.
  """
  def changeset(edge, attrs) do
    edge
    |> cast(attrs, [:since, :from_uid, :to_uid, :graph_id])
    |> validate_required([:from_uid, :to_uid, :graph_id])
  end
end
