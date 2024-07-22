defmodule DB.Edge do
  use Ecto.Schema

  @primary_key {:uid, Ecto.UUID, autogenerate: true}
  schema "edge" do
    field :since, :integer, default: 0
    field :from_uid, Ecto.UUID
    field :to_uid, Ecto.UUID
    field :graph_id, :binary_id

    timestamps()
  end
end
