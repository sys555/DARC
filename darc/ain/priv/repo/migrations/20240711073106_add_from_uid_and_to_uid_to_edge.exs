defmodule DB.Repo.Migrations.AddFromUidAndToUidToEdge do
  use Ecto.Migration

  def change do
    alter table(:edge) do
      add :from_uid, :uuid
      add :to_uid, :uuid
    end
  end
end
