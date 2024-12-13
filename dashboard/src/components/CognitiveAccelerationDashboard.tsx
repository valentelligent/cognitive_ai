import React, { useEffect, useState } from 'react';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  AreaChart, Area, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar,
  ComposedChart, Bar, Scatter, ScatterChart, ZAxis, Cell, Pie, PieChart
} from 'recharts';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs';
import { Select, SelectTrigger, SelectValue, SelectContent, SelectItem } from '@/components/ui/select';
import { Button } from '@/components/ui/button';
import { Slider } from '@/components/ui/slider';
import { format } from 'date-fns';

interface MetricsData {
  timestamp: string;
  acceleration: {
    typing_speed: number;
    error_recovery: number;
    context_switching: number;
    problem_solving: number;
  };
  patterns: {
    recognition_speed: number;
    integration_speed: number;
    pattern_complexity: number;
  };
  growth: {
    acceleration_trend: number;
    learning_efficiency: number;
    adaptability: number;
  };
  meta_patterns: {
    learning_acceleration: number;
    pattern_recognition_evolution: number;
    integration_speed_changes: number;
    adaptability_growth: number;
  };
  cognitive_load: {
    intrinsic: number;
    extraneous: number;
    germane: number;
    total: number;
  };
  flow_state: {
    depth: number;
    duration: number;
    quality: number;
  };
  context: {
    activity_type: string;
    complexity: number;
    focus_score: number;
  };
}

const CognitiveAccelerationDashboard: React.FC = () => {
  const [metricsHistory, setMetricsHistory] = useState<MetricsData[]>([]);
  const [ws, setWs] = useState<WebSocket | null>(null);
  const [timeRange, setTimeRange] = useState('1h');
  const [selectedMetric, setSelectedMetric] = useState('growth');
  const [isFlowState, setIsFlowState] = useState(false);

  useEffect(() => {
    const websocket = new WebSocket('ws://localhost:8000/ws');
    
    websocket.onmessage = (event) => {
      const newMetrics = JSON.parse(event.data);
      setMetricsHistory(prev => [...prev.slice(-50), newMetrics]);
      
      // Detect flow state
      const flowThreshold = 0.8;
      setIsFlowState(newMetrics.flow_state.quality > flowThreshold);
    };
    
    setWs(websocket);
    
    return () => {
      websocket.close();
    };
  }, []);

  const calculateGrowthRate = (data: MetricsData[]) => {
    if (data.length < 2) return 0;
    const latest = data[data.length - 1];
    const previous = data[data.length - 2];
    return ((latest.growth.acceleration_trend - previous.growth.acceleration_trend) / 
            previous.growth.acceleration_trend) * 100;
  };

  return (
    <div className="p-4 space-y-4">
      {/* Header with Controls */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold">Cognitive Growth Dashboard</h1>
          <p className="text-muted-foreground">Real-time cognitive metrics and analysis</p>
        </div>
        <div className="flex gap-4">
          <Select value={timeRange} onValueChange={setTimeRange}>
            <SelectTrigger>
              <SelectValue placeholder="Time Range" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="1h">Last Hour</SelectItem>
              <SelectItem value="4h">Last 4 Hours</SelectItem>
              <SelectItem value="12h">Last 12 Hours</SelectItem>
              <SelectItem value="24h">Last 24 Hours</SelectItem>
            </SelectContent>
          </Select>
          <Button variant={isFlowState ? "default" : "outline"}>
            {isFlowState ? " Flow State Active" : "Regular State"}
          </Button>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className={isFlowState ? "border-blue-500" : ""}>
          <CardHeader>
            <CardTitle>Growth Rate</CardTitle>
            <CardDescription>Overall learning acceleration</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold mb-2">
              {calculateGrowthRate(metricsHistory).toFixed(2)}%
            </div>
            <Progress 
              value={calculateGrowthRate(metricsHistory)} 
              className="h-2"
            />
            <div className="mt-2 text-sm text-muted-foreground">
              {calculateGrowthRate(metricsHistory) > 0 ? "Increasing" : "Decreasing"}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Cognitive Load</CardTitle>
            <CardDescription>Current mental workload</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-[100px]">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={[
                      { name: 'Intrinsic', value: metricsHistory[metricsHistory.length - 1]?.cognitive_load.intrinsic || 0 },
                      { name: 'Extraneous', value: metricsHistory[metricsHistory.length - 1]?.cognitive_load.extraneous || 0 },
                      { name: 'Germane', value: metricsHistory[metricsHistory.length - 1]?.cognitive_load.germane || 0 },
                    ]}
                    cx="50%"
                    cy="50%"
                    innerRadius={25}
                    outerRadius={40}
                    dataKey="value"
                  >
                    <Cell fill="#8884d8" />
                    <Cell fill="#82ca9d" />
                    <Cell fill="#ffc658" />
                  </Pie>
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div className="grid grid-cols-3 gap-2 text-sm mt-2">
              <div className="text-center">
                <div className="font-medium">Intrinsic</div>
                <div className="text-muted-foreground">{(metricsHistory[metricsHistory.length - 1]?.cognitive_load.intrinsic || 0).toFixed(1)}%</div>
              </div>
              <div className="text-center">
                <div className="font-medium">Extraneous</div>
                <div className="text-muted-foreground">{(metricsHistory[metricsHistory.length - 1]?.cognitive_load.extraneous || 0).toFixed(1)}%</div>
              </div>
              <div className="text-center">
                <div className="font-medium">Germane</div>
                <div className="text-muted-foreground">{(metricsHistory[metricsHistory.length - 1]?.cognitive_load.germane || 0).toFixed(1)}%</div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Flow State</CardTitle>
            <CardDescription>Current cognitive state quality</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold mb-2">
              {(metricsHistory[metricsHistory.length - 1]?.flow_state.quality || 0).toFixed(2)}
            </div>
            <Progress 
              value={metricsHistory[metricsHistory.length - 1]?.flow_state.quality * 100 || 0}
              className="h-2"
            />
            <div className="flex justify-between mt-2 text-sm">
              <span>Depth: {(metricsHistory[metricsHistory.length - 1]?.flow_state.depth || 0).toFixed(1)}</span>
              <span>Duration: {format(metricsHistory[metricsHistory.length - 1]?.flow_state.duration || 0, 'mm:ss')}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Context</CardTitle>
            <CardDescription>Current activity analysis</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <div>
                <div className="text-sm font-medium">Activity</div>
                <div className="text-2xl font-bold">{metricsHistory[metricsHistory.length - 1]?.context.activity_type}</div>
              </div>
              <div>
                <div className="text-sm font-medium">Complexity</div>
                <Progress 
                  value={metricsHistory[metricsHistory.length - 1]?.context.complexity * 100 || 0}
                  className="h-2"
                />
              </div>
              <div>
                <div className="text-sm font-medium">Focus Score</div>
                <div className="text-2xl font-bold">{(metricsHistory[metricsHistory.length - 1]?.context.focus_score || 0).toFixed(2)}</div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Main Analysis Tabs */}
      <Tabs defaultValue="overview" className="mt-6">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="patterns">Patterns</TabsTrigger>
          <TabsTrigger value="growth">Growth</TabsTrigger>
          <TabsTrigger value="flow">Flow Analysis</TabsTrigger>
        </TabsList>

        <TabsContent value="overview">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {/* Growth Trajectory Chart */}
            <Card>
              <CardHeader>
                <CardTitle>Cognitive Growth Trajectory</CardTitle>
                <CardDescription>Tracking learning and adaptation over time</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-[400px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <ComposedChart data={metricsHistory}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis 
                        dataKey="timestamp" 
                        tickFormatter={(value) => format(new Date(value), 'HH:mm')}
                      />
                      <YAxis />
                      <Tooltip 
                        labelFormatter={(value) => format(new Date(value), 'HH:mm:ss')}
                      />
                      <Legend />
                      <Area
                        type="monotone"
                        dataKey="growth.acceleration_trend"
                        fill="#8884d8"
                        stroke="#8884d8"
                        fillOpacity={0.3}
                        name="Acceleration"
                      />
                      <Line
                        type="monotone"
                        dataKey="growth.learning_efficiency"
                        stroke="#82ca9d"
                        name="Efficiency"
                      />
                      <Scatter
                        dataKey="growth.adaptability"
                        fill="#ff7300"
                        name="Adaptation Points"
                      />
                    </ComposedChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>

            {/* Pattern Recognition Radar */}
            <Card>
              <CardHeader>
                <CardTitle>Pattern Recognition Analysis</CardTitle>
                <CardDescription>Multi-dimensional pattern analysis</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-[400px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <RadarChart data={[metricsHistory[metricsHistory.length - 1]]}>
                      <PolarGrid />
                      <PolarAngleAxis dataKey="name" />
                      <PolarRadiusAxis />
                      <Radar
                        name="Recognition"
                        dataKey="patterns.recognition_speed"
                        stroke="#8884d8"
                        fill="#8884d8"
                        fillOpacity={0.6}
                      />
                      <Radar
                        name="Integration"
                        dataKey="patterns.integration_speed"
                        stroke="#82ca9d"
                        fill="#82ca9d"
                        fillOpacity={0.6}
                      />
                      <Radar
                        name="Complexity"
                        dataKey="patterns.pattern_complexity"
                        stroke="#ffc658"
                        fill="#ffc658"
                        fillOpacity={0.6}
                      />
                      <Legend />
                    </RadarChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="patterns">
          <div className="grid grid-cols-1 gap-4">
            <Card>
              <CardHeader>
                <CardTitle>Meta-Pattern Evolution</CardTitle>
                <CardDescription>Long-term learning and adaptation patterns</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-[400px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={metricsHistory}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis 
                        dataKey="timestamp"
                        tickFormatter={(value) => format(new Date(value), 'HH:mm')}
                      />
                      <YAxis />
                      <Tooltip 
                        labelFormatter={(value) => format(new Date(value), 'HH:mm:ss')}
                      />
                      <Legend />
                      <Line
                        type="monotone"
                        dataKey="meta_patterns.learning_acceleration"
                        stroke="#8884d8"
                        name="Learning Acceleration"
                      />
                      <Line
                        type="monotone"
                        dataKey="meta_patterns.pattern_recognition_evolution"
                        stroke="#82ca9d"
                        name="Pattern Recognition"
                      />
                      <Line
                        type="monotone"
                        dataKey="meta_patterns.integration_speed_changes"
                        stroke="#ffc658"
                        name="Integration Speed"
                      />
                      <Line
                        type="monotone"
                        dataKey="meta_patterns.adaptability_growth"
                        stroke="#ff7300"
                        name="Adaptability"
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="growth">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <Card>
              <CardHeader>
                <CardTitle>Learning Efficiency Analysis</CardTitle>
                <CardDescription>Detailed breakdown of learning patterns</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-[400px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <ScatterChart>
                      <CartesianGrid />
                      <XAxis 
                        type="number" 
                        dataKey="growth.learning_efficiency" 
                        name="Efficiency"
                      />
                      <YAxis 
                        type="number" 
                        dataKey="growth.adaptability" 
                        name="Adaptability"
                      />
                      <ZAxis 
                        type="number" 
                        dataKey="growth.acceleration_trend" 
                        range={[50, 400]} 
                        name="Acceleration"
                      />
                      <Tooltip cursor={{ strokeDasharray: '3 3' }} />
                      <Legend />
                      <Scatter 
                        name="Growth Patterns" 
                        data={metricsHistory} 
                        fill="#8884d8"
                      />
                    </ScatterChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Cognitive Load Distribution</CardTitle>
                <CardDescription>Analysis of mental workload components</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-[400px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={metricsHistory}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis 
                        dataKey="timestamp"
                        tickFormatter={(value) => format(new Date(value), 'HH:mm')}
                      />
                      <YAxis />
                      <Tooltip 
                        labelFormatter={(value) => format(new Date(value), 'HH:mm:ss')}
                      />
                      <Legend />
                      <Area
                        type="monotone"
                        dataKey="cognitive_load.intrinsic"
                        stackId="1"
                        stroke="#8884d8"
                        fill="#8884d8"
                        name="Intrinsic Load"
                      />
                      <Area
                        type="monotone"
                        dataKey="cognitive_load.extraneous"
                        stackId="1"
                        stroke="#82ca9d"
                        fill="#82ca9d"
                        name="Extraneous Load"
                      />
                      <Area
                        type="monotone"
                        dataKey="cognitive_load.germane"
                        stackId="1"
                        stroke="#ffc658"
                        fill="#ffc658"
                        name="Germane Load"
                      />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="flow">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <Card>
              <CardHeader>
                <CardTitle>Flow State Analysis</CardTitle>
                <CardDescription>Deep work and focus patterns</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-[400px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <ComposedChart data={metricsHistory}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis 
                        dataKey="timestamp"
                        tickFormatter={(value) => format(new Date(value), 'HH:mm')}
                      />
                      <YAxis />
                      <Tooltip 
                        labelFormatter={(value) => format(new Date(value), 'HH:mm:ss')}
                      />
                      <Legend />
                      <Area
                        type="monotone"
                        dataKey="flow_state.quality"
                        fill="#8884d8"
                        stroke="#8884d8"
                        fillOpacity={0.3}
                        name="Flow Quality"
                      />
                      <Line
                        type="monotone"
                        dataKey="flow_state.depth"
                        stroke="#82ca9d"
                        name="Flow Depth"
                      />
                      <Bar
                        dataKey="flow_state.duration"
                        fill="#ffc658"
                        name="Duration"
                        barSize={20}
                      />
                    </ComposedChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Focus Analysis</CardTitle>
                <CardDescription>Attention and concentration metrics</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-[400px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={metricsHistory}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis 
                        dataKey="timestamp"
                        tickFormatter={(value) => format(new Date(value), 'HH:mm')}
                      />
                      <YAxis />
                      <Tooltip 
                        labelFormatter={(value) => format(new Date(value), 'HH:mm:ss')}
                      />
                      <Legend />
                      <Line
                        type="monotone"
                        dataKey="context.focus_score"
                        stroke="#8884d8"
                        name="Focus Score"
                      />
                      <Line
                        type="monotone"
                        dataKey="context.complexity"
                        stroke="#82ca9d"
                        name="Task Complexity"
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default CognitiveAccelerationDashboard;
