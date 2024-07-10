defmodule DB.Actor do
  use Ecto.Schema

  @primary_key {:uid, Ecto.UUID, autogenerate: true}
  schema "actor" do
    field :name, :string
    field :role, :string
    field :age, :integer
    field :graph_id, Ecto.UUID

    timestamps()
  end
end
