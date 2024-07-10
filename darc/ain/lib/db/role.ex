defmodule DB.Role do
  use Ecto.Schema

  @primary_key {:uid, Ecto.UUID, autogenerate: true}
  schema "role" do
    field :name, :string
    field :type, :string
    field :action, :string

    timestamps()
  end
end
