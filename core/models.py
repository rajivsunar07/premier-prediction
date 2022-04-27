from django.db import models

# Create your models here.

class Fixtures(models.Model):
    id = models.IntegerField(max_length=250, primary_key=True)
    team_a = models.IntegerField(max_length=250)
    team_h = models.IntegerField(max_length=250)
    team_h_difficulty = models.IntegerField(max_length=250)
    team_a_difficulty = models.IntegerField(max_length=250)
    team_a_wins = models.IntegerField(max_length=250)
    team_h_wins = models.IntegerField(max_length=250)
    team_a_loss = models.IntegerField(max_length=250)
    team_h_loss = models.IntegerField(max_length=250)
    team_a_draw = models.IntegerField(max_length=250)
    team_h_draw = models.IntegerField(max_length=250)
    team_a_form = models.IntegerField(max_length=250)
    team_h_form = models.IntegerField(max_length=250)
    past_a_wins = models.IntegerField(max_length=250)
    past_h_wins = models.IntegerField(max_length=250)
    past_a_loss = models.IntegerField(max_length=250)
    past_h_loss = models.IntegerField(max_length=250)
    past_a_draw = models.IntegerField(max_length=250)
    past_h_draw = models.IntegerField(max_length=250)

    team_a_score = models.FloatField(max_length=250, null=True)
    team_h_score = models.FloatField(max_length=250, null=True)
    exp_goals_h = models.FloatField(max_length=250)
    exp_goals_a = models.FloatField(max_length=250)
    highest_goal_a = models.FloatField(max_length=250)
    highest_a = models.FloatField(max_length=250)
    second_goal_a = models.FloatField(max_length=250)
    second_a = models.FloatField(max_length=250)
    third_goal_a = models.FloatField(max_length=250)
    third_a = models.FloatField(max_length=250)
    highest_goal_h = models.FloatField(max_length=250)
    highest_h = models.FloatField(max_length=250)
    second_goal_h = models.FloatField(max_length=250)
    second_h = models.FloatField(max_length=250)
    third_goal_h = models.FloatField(max_length=250)
    third_h = models.FloatField(max_length=250)
    event = models.FloatField(max_length=250, null=True)


    finished = models.BooleanField(max_length=250)
    started = models.BooleanField(max_length=250, null=True)

    kickoff_time = models.TextField(null=True)
    stats = models.TextField()
    ftr = models.TextField(null=True)



class Teams(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.TextField()
    short_name = models.TextField()


    













  

    def __str__(self):
        return self.name