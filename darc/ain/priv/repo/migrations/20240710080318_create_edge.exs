defmodule DB.Repo.Migrations.CreateEdge do
  use Ecto.Migration

  def change do
    create table(:edge, primary_key: false) do
      add :uid, :uuid, primary_key: true
      add :since, :integer, default: 0
      add :graph_id, :uuid
    end
  end
end
