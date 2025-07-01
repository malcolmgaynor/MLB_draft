library(dplyr)
library(ggplot2)
library(earth)
library(caret)


# read in the pre-merged data from Python 
training_data = read.csv(file=file.choose())
df_4 = read.csv(file=file.choose())

# X coefficients
formars1<-data.frame(training_data$number, training_data$hs, training_data$fv, training_data$risk,
                     training_data$position_1B,training_data$position_C,training_data$position_CF,
                     training_data$position_IF,training_data$position_LHP,training_data$position_OF,
                     training_data$position_RHP,training_data$position_SS)

# X coefficients for testing 
formars_testing <- data.frame(df_4$number, df_4$hs, df_4$fv, df_4$risk,
                              df_4$position_1B,df_4$position_C,df_4$position_CF,
                              df_4$position_IF,df_4$position_LHP,df_4$position_OF,
                              df_4$position_RHP,df_4$position_SS)

# fit the first mars model (no second order terms)
mars1 <- earth(training_data$pct_max_bonus~., data = formars1)

# summary includes Rsquared, along with coefficeints
summary(mars1) # in sample rsquared of 0.934462 

# now we do out of sample r-squared, calculated manually: 

ypreds <- predict(mars1, newdata = formars_testing)
ytrue <- df_4$pct_max_bonus

# sum of squared differences between actual and predicted values 
rss <- sum((ytrue - ypreds)^2)

# sumo of squared differneces between actual and mean from TRAINING (naive predictions)
tss <- sum((ytrue - mean(training_data$pct_max_bonus))^2)

# Calculate out-of-sample R-squared
r2_oos <- 1 - (rss/tss)

print("out of sample r-squared: ")
print(r2_oos) # really, really strong 0.9!!!

# now, we include squared interaction terms as well, just to see: 

mars2 <- earth(training_data$pct_max_bonus~., data = formars1,degree=2)

# summary includes Rsquared, along with coefficeints
summary(mars2) # in sample rsquared of 0.95 

# now we do out of sample r-squared, calculated manually: 

ypreds2 <- predict(mars2, newdata = formars_testing)
ytrue <- df_4$pct_max_bonus

# sum of squared differences between actual and predicted values 
rss2 <- sum((ytrue - ypreds2)^2)

# Calculate out-of-sample R-squared (note: tss stays the same )
r2_oos2 <- 1 - (rss2/tss)

print("out of sample r-squared: ")
print(r2_oos2) # even stronger 0.93!!!

# Now, for use in the formulation, for each player, we need 
# to know their signing bonus given each number they were predicted. 

# creating signing bonus dataframe (0s for now)
signing_bonus_df <- data.frame(matrix(0, nrow = nrow(df_4), ncol = max(df_4$number) + 1))

# first column is player name
signing_bonus_df[, 1] <- df_4$name

# name columns by pick number 
colnames(signing_bonus_df) <- c("name", paste0("pick_", 1:max(df_4$number)))

for(i in 1:nrow(df_4)){                   # is each player 
  for(j in 1:max(df_4$number)){            # j is each pick 
    this_row = formars_testing[i,]         # this player
    this_row$df_4.number = j               # at this pick 
    signing_bonus = predict(mars2, newdata=this_row) # predict their signing bonus 
    signing_bonus_df[i,j+1] <- signing_bonus[1] # append prediction to the new df
  }
}

View(signing_bonus_df) #Note: we may need need to map anything over 1 to 1, if that becomes an issue, or do log reg instead...

write.csv(signing_bonus_df, "signing_bonus_df.csv", row.names = FALSE)