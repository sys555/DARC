defmodule DB.Repo.Migrations.AddTimestampsToEdge do
  use Ecto.Migration

  def change do
    alter table(:edge) do
      add :inserted_at, :naive_datetime, null: false, default: fragment("now()")
      add :updated_at, :naive_datetime, null: false, default: fragment("now()")
    end
  end
end
