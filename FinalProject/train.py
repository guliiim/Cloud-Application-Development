import tensorflow as tf
from tensorflow.keras.layers import Embedding, Flatten, Dot, Dense, Input
from tensorflow.keras.models import Model
import numpy as np

user_ids = user_item_df['user_id'].unique()
item_ids = user_item_df['item_id'].unique()

user_to_index = {user: idx for idx, user in enumerate(user_ids)}
item_to_index = {item: idx for idx, item in enumerate(item_ids)}

user_item_df['user_idx'] = user_item_df['user_id'].map(user_to_index)
user_item_df['item_idx'] = user_item_df['item_id'].map(item_to_index)

num_users = len(user_ids)
num_items = len(item_ids)

user_indices = user_item_df['user_idx'].values
item_indices = user_item_df['item_idx'].values
ratings = user_item_df['rating'].values

train_size = int(0.8 * len(ratings))
user_train, user_test = user_indices[:train_size], user_indices[train_size:]
item_train, item_test = item_indices[:train_size], item_indices[train_size:]
rating_train, rating_test = ratings[:train_size], ratings[train_size:]

def create_model(num_users, num_items, embedding_dim=50):
    user_input = Input(shape=(1,), name='user')
    item_input = Input(shape=(1,), name='item')

    user_embedding = Embedding(num_users, embedding_dim, input_length=1)(user_input)
    item_embedding = Embedding(num_items, embedding_dim, input_length=1)(item_input)

    user_vector = Flatten()(user_embedding)
    item_vector = Flatten()(item_embedding)

    dot_product = Dot(axes=1)([user_vector, item_vector])
    output = Dense(1, activation='relu')(dot_product)

    model = Model(inputs=[user_input, item_input], outputs=output)
    model.compile(optimizer='adam', loss='mse', metrics=['mae'])
    return model

model = create_model(num_users, num_items)
model.fit([user_train, item_train], rating_train, epochs=10, batch_size=16)

model.save('event_recommendation_model')
