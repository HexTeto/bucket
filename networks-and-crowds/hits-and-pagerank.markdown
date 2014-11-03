## HITS

```
E1.

有 [A,E] 五家餐馆, [a,d] 四位顾客, 他们可以选择任意一家或多家餐馆进行推荐.
假设有推荐矩阵如下:
-------------------- +
    a    b    c    d |  G     S
A   *         *    * |  3    21
B   *    *    *      |  3    20
C        *           |  1     6
D   *              * |  2    15
E        *         * |  2    13
-------------------- +

L   8    6    6    7

有矩阵得知, 餐馆 A 被 a, c, d, 三人推荐, 因此有得票数 G(A) = 3,
同理其它餐馆得票数如 G 列所列.

此时可以看到 A 和 B 的得票数都为 3; D 和 E 的得票数都为 2;
我们无法完全区分, 于是可以反过来根据得票数对推荐人 [a,d] 进行打分,
a 推荐了 A, B, D, 它们的得票分别为 3, 3, 2, 于是有推荐人得分 L(a) = 3 + 3 + 2 = 8,
同理其它推荐人得分如 L 行所列.

根据 "水平更高的推荐人推荐的餐馆更可信" 这一合理假设,
于是可以将同一餐馆的不同推荐人得分相加,
如 a, c, d 都推荐了 A; L(a) = 8, L(c) = 6, L(d) = 7.
于是得到 S(A) = 8 + 6 + 7 = 21.
同理其它得分如 S 列所列.

由 S 我们得到了 [A,E] 的完全区分, 即推荐顺序为 [A, B, D, E, C].
```

`E1` 中所示推荐方法称之为 __反复改进原则 (principle of repeated improvement)__.
其基本思路就是在获得初始的无法完全区分的得分之后, 反过来利用该得分对推荐者评估,
然后在考虑推荐者分值的情况下求得一个加权评分.
这个计算过程可以反复迭代, 直到得到可以完全区分的无重结果.

在万维网中, 我们通常认为一个网页
- 被很多网页指向: __权威性高__
- 指向很多网页: __中枢性强__

__"Hyperlink-Induced Topic Search, HITS"__ 算法,
该算法就是利用网页的权威值 (auth) 和中枢值 (hub) 来进行推荐.

```
####
# array auth[page]
# array hub[page]
# dict digraph {nodes: {edges}}
# function hits(graph)
####

# Alg HITS:
# Input a digraph

# Initialization
for each node p (a web page) in digraph:
    auth[p] = 1, hub[p] = 1

for k times:
    # Update auth using hub
    for each p:
        q = {p.indeg()}
        auth[p] = Σ(hub[q])

    # Update hub using auth
    for each p:
        q = {p.outdeg()}
        hub[p] = Σ(auth[q])

return sort(digraph, auth)
```

观察 pseudo 发现, 每个网页的权威值和中枢值会随着迭代进行而递增,
对于互联网这种无比庞大的有向图数据来说显然该算法需要非常高的计算消耗.
因为 auth 和 hub 它们的值的意义在于它们彼此的相对大小,
于是就可以采用 __归一化与极限__ 的方法来控制函数的收敛,
即每一轮计算后, 将结果做归一化处理, 随着迭代进行, 这些结果最终会趋向于一个稳定的极限.

```python
def compute_in_edges(digraph):

    result = {node: set() for node in digraph.keys()}
    for node in digraph:
        for edge in digraph[node]:
            if edge not in result.keys():
                result[edge] = set()
            else:
                result[edge].add(node)
    return result


def improved_hits(digraph):

    auth = {page: 1 for page in digraph}
    hub = auth.copy()
    prev_auth = auth.copy()
    prev_hub = hub.copy()
    b_digraph = compute_in_edges(digraph)

    equilibrium = False
    while not equilibrium:
        for node_p in digraph.keys():
            nodes_q = b_digraph[node_p]
            auth[node_p] = sum([hub[node_q] for node_q in nodes_q])

        for node_p in digraph.keys():
            nodes_q = digraph[node_p]
            hub[node_p] = sum([auth[node_q] for node_q in nodes_q])

        total_auth = sum(auth.values())
        total_hub = sum(hub.values())
        for idx in digraph:
            auth[idx] /= total_auth
            hub[idx] /= total_hub

        if auth == prev_auth and hub == prev_hub:
            equilibrium = True
        prev_auth = auth.copy()
        prev_hub = hub.copy()

    return (auth, hub)
```




## PageRank

基本思想:
1. 对于一个由 `n` 个节点的有向图描述的网络, 设所有节点的初始值为 `1/n`.
2. 每一个节点将自己的当前值均分给所有它所指向的相邻节点 (若没指向任何节点, 则视为自传递).
3. 每一个节点的值更新为它从指向它的相邻节点所收到的值的和 (同样包括自传递可能).
4. 反复迭代 2, 3 计算过程直到结果收敛.

> 在 PageRank 算法中, 每次迭代的结果相加之和恒等于 __初始值之和__


### 同比缩减和等量补偿

基本的 PageRank 算法在某些特殊结构上会存在一些缺陷,
比如两个节点互相都仅指向对方, 那么当存在任意一条其它路径指向它们中任意一个节点时.
这两个节点就会不断掠夺其它所有节点的 PR 值,
最终导致的结果就是这两个节点分别趋向 `0.5` 而其它所有节点趋向 `0`.

为了解决这样的缺陷, PageRank 算法又引入了一个比例因子参数 `s (0 < s < 1)`,
通过使用 `s` 进行同比缩减和统一补偿来防止 PR 值过度集中到个别节点上

- 同比缩减: 在每次更新 PR 值后, 将每个节点的 PR 值乘以比例因子 `s`.
- 统一补偿: 在每一节点的 PR 值上统一加上 `(1 - s) / n`.

通过观察可以看到, 该方法实际上就是使得拥有较大 PR 值的节点在同比缩减时损失较多的值,
而拥有较小 PR 值的节点相对就损失得小, 并有可能通过统一补偿实现净增加.
