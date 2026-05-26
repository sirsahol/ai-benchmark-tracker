import './styles/design-tokens.css';
import './styles/theme-dark.css';
import './styles/theme-light.css';
import './styles/base.css';
import './styles/components.css';
import { mount } from 'svelte';
import App from './App.svelte';

const app = mount(App, { target: document.body });
export default app;
