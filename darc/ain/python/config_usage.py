import uuid
from darc.ain.python.mas import MAS  

def main():
    db_url = 'postgresql+psycopg2://postgres:123456@localhost:5432/ain_repo'
    
    # config = {
    #     "role": [
    #         "DatasetDB",
    #         "Attacker",
    #         "Filter",
    #         "LLM_with_PPL",
    #         "AttackEvaluator",
    #         "LeaderBoard",
    #     ],
    #     "edge": [
    #         ("DatasetDB", "Attacker"),
    #         ("DatasetDB", "Filter"),
    #         ("DatasetDB", "AttackEvaluator"),
    #         ("Attacker", "DatasetDB"),
    #         ("Attacker", "Filter"),
    #         ("Filter", "LLM_with_PPL"),
    #         ("Filter", "Attacker"),
    #         ("LLM_with_PPL", "AttackEvaluator"),
    #         ("AttackEvaluator", "DatasetDB"),
    #         ("AttackEvaluator", "LeaderBoard"),
    #     ],
    #     "args": [
    #         ("DatasetDB", 1),
    #         ("LLM_with_PPL", 2),
    #         ("Attacker", 2),
    #     ],
    # }
    config = {
        "role": [
            "Admin",
            "User",
        ],
        "edge": [
            ("Admin", "User"),
        ],
        "args": [
            ("Admin", 1),
            ("User", 5),
        ],
    }

    with MAS(db_url) as mas:
        mas.clear_tables()
        mas.config_db(config)

if __name__ == "__main__":
    main()