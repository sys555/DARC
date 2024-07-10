defmodule DB.Repo.Migrations.CreateTask do
  use Ecto.Migration

  create table(:tasks) do
    add :uid, :uuid, null: false
    add :ttl, :integer
    add :nodes, :jsonb
    add :input, :jsonb
    add :output, :jsonb
    add :diff_graph, :jsonb
    add :whole_graph, :jsonb
    add :logs, :jsonb

    timestamps()
  end
end
