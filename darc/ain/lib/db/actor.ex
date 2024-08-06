defmodule DB.Actor do
  use Ecto.Schema
  import Ecto.Changeset

  @primary_key {:uid, Ecto.UUID, autogenerate: false}
  schema "actor" do
    field :name, :string
    field :role, :string
    field :age, :integer
    field :graph_id, Ecto.UUID

    timestamps()
  end

  def changeset(actor, attrs) do
    actor
    |> cast(attrs, [:uid, :name, :role, :age, :graph_id])
    |> ensure_uid()
    |> validate_required([:uid, :name, :role, :age, :graph_id])
  end

  defp ensure_uid(changeset) do
    case get_field(changeset, :uid) do
      nil -> put_change(changeset, :uid, Ecto.UUID.generate())
      _ -> changeset
    end
  end
end
