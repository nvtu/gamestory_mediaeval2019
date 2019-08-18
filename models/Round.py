class Round:
    """
    Contain prior information about a round:
        - When did it start?
        - When did it end?
        - What is that round?
        - What team won the game?
        - What teams were in the game?
        - What is its team id?
    This class does not contain the information of the source video file path
    """

    def __init__(self, round_idx, start_time, end_time, team_1, team_2, ingameTeam_win, team_id_win):
        self.round_idx = round_idx
        self.start_time = start_time
        self.end_time = end_time
        self.team_1 = team_1
        self.team_2 = team_2
        self.ingameTeam_win = ingameTeam_win
        self.team_id_win = team_id_win
