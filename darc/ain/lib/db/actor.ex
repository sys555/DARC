defmodule DB.Actor do
  use Ecto.Schema
  import Ecto.Changeset

  @primary_key {:uid, Ecto.UUID, autogenerate: true}
  schema "actor" do
    field :name, :string
    field :role, :string
    field :age, :integer
    field :graph_id, Ecto.UUID

    timestamps()
  end

  def changeset(actor, attrs) do
    actor
    |> cast(attrs, [:name, :role, :age, :graph_id])
    |> validate_required([:name, :role, :age, :graph_id])
  end
end
