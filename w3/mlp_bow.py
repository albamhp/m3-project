import os
import argparse

import numpy as np
from PIL import Image
from sklearn.feature_extraction import image
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.svm import SVC
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import GridSearchCV, RandomizedSearchCV
from keras.models import Model, load_model

from utils import load_dataset
from model import BoWTransformer, histogram_intersection_kernel
from utils import Timer


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dataset_dir', type=str, default='/home/mcv/datasets/MIT_split')
    parser.add_argument('--num_patches', type=int, default=128)
    parser.add_argument('--model_file', type=str, required=True)
    return parser.parse_args()


class MLP:
    def __init__(self, model_file, num_patches):
        model = load_model(model_file)
        model = Model(inputs=model.input, outputs=model.layers[-2].output)
        print(model.summary())
        self.model = model
        self.patch_size = model.layers[0].input.shape[1:3]
        self.num_patches = num_patches

    def compute(self, image_files):
        descriptors = []
        for image_file in image_files:
            patches = self._extract_patches(image_file)
            des = self.model.predict(patches / 255., batch_size=self.num_patches)
            descriptors.append(des)
        return descriptors

    def _extract_patches(self, image_file):
        img = Image.open(image_file)
        patches = image.extract_patches_2d(np.array(img), self.patch_size, max_patches=self.num_patches)
        return patches


def train(args):
    train_filenames, train_labels = load_dataset(os.path.join(args.dataset_dir, 'train'))
    test_filenames, test_labels = load_dataset(os.path.join(args.dataset_dir, 'test'))

    model = MLP(args.model_file, args.num_patches)

    with Timer('Extract train descriptors'):
        train_descriptors = model.compute(train_filenames)
    with Timer('Extract test descriptors'):
        test_descriptors = model.compute(test_filenames)

    le = LabelEncoder()
    le.fit(train_labels)
    train_labels = le.transform(train_labels)
    test_labels = le.transform(test_labels)

    transformer = BoWTransformer(n_clusters=760, n_samples=100000, norm='power')
    scaler = StandardScaler(copy=False)
    classifier = SVC(C=1, kernel=histogram_intersection_kernel, gamma=.001)
    pipeline = make_pipeline(transformer, scaler, classifier)

    param_grid = {
        'svc__C': np.logspace(-3, 15, 5, base=2),
        'svc__kernel': ['linear', 'rbf', 'sigmoid'],
        'svc__gamma': np.logspace(-15, 3, 5, base=2)
    }
    cv = GridSearchCV(pipeline, param_grid, n_jobs=-1, cv=3, refit=True, verbose=11)

    with Timer('Train'):
        cv.fit(train_descriptors, train_labels)

    with Timer('Test'):
        accuracy = cv.score(test_descriptors, test_labels)

    print('Best params: {}'.format(cv.best_params_))
    print('Accuracy: {}'.format(accuracy))


def main():
    args = parse_args()
    train(args)


if __name__ == '__main__':
    main()
