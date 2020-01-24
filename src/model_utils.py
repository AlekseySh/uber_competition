import numpy as np
from catboost import CatBoostClassifier, Pool
from sklearn.metrics import f1_score


class FlexibleF1(object):

    def __init__(self,
                 th_start: float = 0.0,
                 th_stop: float = 1.0,
                 steps: int = 20
                 ):
        self.th_grid = np.linspace(start=th_start,
                                   stop=th_stop,
                                   num=steps
                                   )
        self.train_call = False

    @staticmethod
    def is_max_optimal() -> bool:
        return True

    @staticmethod
    def get_final_error(error, _):
        return error

    def evaluate(self, approxes, target, _) -> float:
        self.train_call = ~self.train_call

        if self.train_call:
            return 0, 1.0

        else:
            assert len(approxes) == 1
            assert len(target) == len(approxes[0])

            approx = np.array(approxes[0])

            exps = np.exp(approx)
            probs = exps / (1 + exps)

            scores = [f1_score(y_pred=probs > th,
                               y_true=np.array(target)
                               )
                      for th in self.th_grid]

            score = max(scores)

            return score, 1.0


def get_data():
    cat_features = [0, 1, 2]

    train_data = [["a", "b", 1, 4, 5, 6],
                  ["a", "b", 4, 5, 6, 7],
                  ["c", "d", 30, 40, 50, 60]]

    train_labels = [1, 1, 0]

    eval_data = [["a", "c", 3, 4, 4, 1],
                 ["a", "d", 1, 5, 5, 5],
                 ["b", "d", 31, 25, 60, 70],
                 ["b", "a", 31, 1, 60, 70],
                 ["b", "a", 31, 1, 2, 1]]

    eval_labels = [0, 1, 1, 0, 1]

    eval_dataset = Pool(eval_data,
                        label=eval_labels,
                        cat_features=cat_features)

    return train_data, train_labels, eval_data, eval_labels, eval_dataset, cat_features


def check_flexible():
    train_data, train_labels, eval_data, eval_labels, eval_dataset, cat_features = get_data()

    # Initialize CatBoostClassifier with custom `eval_metric`
    flexible_f1 = FlexibleF1(0.1, 0.7, 10)
    model = CatBoostClassifier(iterations=5,
                               eval_metric=flexible_f1,
                               loss_function='Logloss')

    # Fit model with `use_best_model=True`
    model.fit(train_data,
              train_labels,
              cat_features,
              use_best_model=True,
              eval_set=eval_dataset)

    # Get predictions
    pred = model.predict_proba(eval_data)

    scores = [f1_score(y_pred=pred[:, 1] > th,
                       y_true=np.array(eval_labels)
                       )
              for th in flexible_f1.th_grid]

    score = max(scores)
    print('score', score)


def check_th():
    train_data, train_labels, eval_data, eval_labels, eval_dataset, cat_features = get_data()

    # Initialize CatBoostClassifier with custom `eval_metric`
    th_f1 = FlexibleF1(0.5, 0.5, 1)
    n_it = 5
    model = CatBoostClassifier(iterations=n_it,
                               eval_metric=th_f1,
                               loss_function='Logloss')

    # Fit model with `use_best_model=True`
    model.fit(train_data,
              train_labels,
              cat_features,
              use_best_model=True,
              eval_set=eval_dataset)

    # lib version
    model2 = CatBoostClassifier(iterations=n_it,
                                eval_metric='F1',
                                loss_function='Logloss')

    # Fit model with `use_best_model=True`
    model2.fit(train_data,
               train_labels,
               cat_features,
               use_best_model=True,
               eval_set=eval_dataset)


if __name__ == '__main__':
    check_flexible()
    check_th()
