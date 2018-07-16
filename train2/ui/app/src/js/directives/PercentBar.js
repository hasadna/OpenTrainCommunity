export default function RexPercentBar(env) {
    'ngInject';
    return {
        restrict: 'E',
        scope: {
          value: '=value',
          type: '=type'
        },
        templateUrl: env.baseDir + '/tpls/PercentBar.html'
      };
};


