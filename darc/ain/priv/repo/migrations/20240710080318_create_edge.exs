defmodule DB.Repo.Migrations.CreateEdge do
  use Ecto.Migration

  def change do
    create table(:edge, primary_key: false) do
      add :uid, :uuid, primary_key: true
      add :since, :integer, default: 0
      add :graph_id, :uuid

      # 添加 from_uid 和 to_uid 字段
      add :from_uid, :uuid
      add :to_uid, :uuid

      timestamps()
    end

    # 添加索引以加快查询速度
    create index(:edge, [:from_uid])
    create index(:edge, [:to_uid])
    create index(:edge, [:graph_id])
  end
end
