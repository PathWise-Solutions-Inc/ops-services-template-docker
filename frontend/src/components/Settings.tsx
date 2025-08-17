import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  Grid,
  Card,
  CardContent,
  Switch,
  FormControlLabel,
  Divider,
} from '@mui/material';
import { Save as SaveIcon } from '@mui/icons-material';

const Settings: React.FC = () => {
  const [settings, setSettings] = useState({
    apiUrl: 'http://localhost',
    apiKey: '',
    maxTokens: 1000,
    temperature: 0.7,
    autoSave: true,
    darkMode: false,
    notifications: true,
  });

  const handleSave = () => {
    localStorage.setItem('ragSettings', JSON.stringify(settings));
    alert('Settings saved successfully!');
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Settings
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                API Configuration
              </Typography>
              <TextField
                fullWidth
                label="API URL"
                value={settings.apiUrl}
                onChange={(e) => setSettings({ ...settings, apiUrl: e.target.value })}
                margin="normal"
              />
              <TextField
                fullWidth
                label="API Key"
                type="password"
                value={settings.apiKey}
                onChange={(e) => setSettings({ ...settings, apiKey: e.target.value })}
                margin="normal"
              />
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Model Settings
              </Typography>
              <TextField
                fullWidth
                label="Max Tokens"
                type="number"
                value={settings.maxTokens}
                onChange={(e) => setSettings({ ...settings, maxTokens: parseInt(e.target.value) })}
                margin="normal"
              />
              <TextField
                fullWidth
                label="Temperature"
                type="number"
                value={settings.temperature}
                onChange={(e) => setSettings({ ...settings, temperature: parseFloat(e.target.value) })}
                margin="normal"
                inputProps={{ min: 0, max: 1, step: 0.1 }}
              />
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Application Preferences
              </Typography>
              <FormControlLabel
                control={
                  <Switch
                    checked={settings.autoSave}
                    onChange={(e) => setSettings({ ...settings, autoSave: e.target.checked })}
                  />
                }
                label="Auto-save settings"
              />
              <FormControlLabel
                control={
                  <Switch
                    checked={settings.darkMode}
                    onChange={(e) => setSettings({ ...settings, darkMode: e.target.checked })}
                  />
                }
                label="Dark mode"
              />
              <FormControlLabel
                control={
                  <Switch
                    checked={settings.notifications}
                    onChange={(e) => setSettings({ ...settings, notifications: e.target.checked })}
                  />
                }
                label="Enable notifications"
              />
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12}>
          <Button
            variant="contained"
            startIcon={<SaveIcon />}
            onClick={handleSave}
            size="large"
          >
            Save Settings
          </Button>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Settings;