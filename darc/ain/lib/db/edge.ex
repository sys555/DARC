defmodule DB.Edge do
  use Ecto.Schema
  import Ecto.Changeset

  @primary_key {:uid, Ecto.UUID, autogenerate: false}
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
    |> cast(attrs, [:uid, :since, :from_uid, :to_uid, :graph_id])
    |> ensure_uid()
    |> validate_required([:uid, :from_uid, :to_uid, :graph_id])
    |> unique_constraint(:uid, name: :edge_pkey)
  end

  defp ensure_uid(changeset) do
    case get_field(changeset, :uid) do
      nil -> put_change(changeset, :uid, Ecto.UUID.generate())
      _ -> changeset
    end
  end
end
