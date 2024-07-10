defmodule DB.Repo.Migrations.CreateRole do
  use Ecto.Migration

  def change do
    create table(:role, primary_key: false) do
      add :uid, :uuid, primary_key: true
      add :name, :string
      add :type, :string
      add :action, :string

      timestamps()
    end
  end
end
