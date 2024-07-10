defmodule DB.Repo.Migrations.CreateActor do
  use Ecto.Migration

  def change do
    create table(:actor, primary_key: false) do
      add :uid, :uuid, primary_key: true
      add :name, :string
      add :role, :string
      add :age, :integer, default: 0
      add :graph_id, :uuid

      timestamps()
    end
  end
end
