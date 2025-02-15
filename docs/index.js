if (typeof system_data == 'object') {
    const system_name = document.getElementById('system_name');
    system_name.innerText = system_data.name;
}

let data = {};


if (typeof rust_data == 'object') {
    data['c_libuv'] = c_libuv_data
}
if (typeof rust_data == 'object') {
    data['rust'] = rust_data
}
if (typeof go_data == 'object') {
    data['go'] = go_data
}
if (typeof bun_data == 'object') {
    data['bun'] = bun_data
}
if (typeof node_data == 'object') {
    data['node'] = node_data
}
if (typeof php_data == 'object') {
    data['php'] = php_data
}
if (typeof python_data == 'object') {
    data['python'] = python_data
}

console.log(system_data)
console.log(data)

const charts_container = document.getElementById('charts_container');



function append_canvas(id) {
    const chart = document.createElement('div');
    chart.style = 'width: 49%; min-width: 400px;'
    charts_container.appendChild(chart);

    const canvas = document.createElement('canvas');
    canvas.id = id;
    canvas.width = 400;
    canvas.height = 200;
    chart.appendChild(canvas);
}

const metrics = ['rps', 'latency_median_ms', 'avg_cpu_percent', 'avg_memory_used_mb'];

metrics.forEach(metric => {
    append_canvas(metric)
    const ctx = document.getElementById(metric).getContext('2d');
    const name = metric.replaceAll('_', ' ')
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: Object.entries(data)[0][1].map(d => d.total_requests),
            datasets: Object.keys(data).map(key => ({
                label: key,
                data: data[key].map(d => d[metric]),
                fill: false
            }))
        },
        options: {
            responsive: true,
            plugins: {
                legend: { position: 'right' },
                title: { display: true, text: name, font: { size: 18 }, },
            },
            scales: {
                x: { title: { display: true, text: 'total requests' } },
                y: { title: { display: true, text: metric } },
            }
        }
    });
});
