function calculPoints(countSecondes, secondes) {
        if (countSecondes <= 1) {
            points = 3;
        }
        if (countSecondes > 1 && countSecondes <=2) {
            points = 2;
        }
        if (countSecondes > 2 && countSecondes <=4) {
            points = 1;
        }
        if (countSecondes > 4) {
            points = 0;
        }
    return points;
}