defmodule DB.Repo.Migrations.CreateTasks do
  use Ecto.Migration

  def change do
    create table(:tasks, primary_key: false) do
      add :uid, :uuid, primary_key: true
      add :ttl, :integer
      add :nodes, :map
      add :input, :map
      add :output, :map
      add :diff_graph, :map
      add :whole_graph, :map
      add :logs, :map

      timestamps()
    end
  end
end
